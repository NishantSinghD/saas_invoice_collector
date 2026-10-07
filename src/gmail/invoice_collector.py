import re
from pathlib import Path
from src.invoices.source_detector import detect_invoice_source
from src.gmail.client import (
    download_attachment,
    get_message,
    get_messages_for_date_range,
)
from src.gmail.parser import (
    extract_message_body,
    get_attachments,
)
from src.invoices.extractor import extract_invoice_data
from src.invoices.output import (
    save_invoice_body_as_pdf,
    save_invoice_pdf,
    write_summary_csv,
)
from src.pipeline import process_invoice_records


def download_pdf_attachments(
    service,
    messages,
    download_directory,
    source_account="",
):
    """Download PDF attachments and retain their email metadata."""

    download_directory = Path(download_directory)
    download_directory.mkdir(parents=True, exist_ok=True)

    downloaded_files = []

    for message_summary in messages:
        message_id = message_summary["id"]
        message = get_message(service, message_id)

        plain_text, _ = extract_message_body(message)

        for attachment in get_attachments(message):
            filename = attachment["filename"]

            is_pdf = (
                attachment.get("mime_type", "").lower()
                == "application/pdf"
                or filename.lower().endswith(".pdf")
            )

            if not is_pdf:
                continue

            content = download_attachment(
                service,
                message_id,
                attachment["attachment_id"],
            )

            safe_filename = re.sub(
                r"[^A-Za-z0-9._-]+",
                "_",
                Path(filename).name,
            )

            destination = download_directory / (
                f"{message_id}_{safe_filename}"
            )
            destination.write_bytes(content)

            downloaded_files.append(
                {
                    "file_path": destination,
                    "source_account": source_account,
                    "source_email_id": message_id,
                    "email_body": plain_text,
                }
            )

    return downloaded_files

def process_email_body_invoices(
    service,
    messages,
    output_directory,
    source_account="",
):
    """Process invoices whose details are contained in the email body."""

    invoices = []

    for message_summary in messages:
        message_id = message_summary["id"]

        message = get_message(
            service,
            message_id,
        )

        plain_text, _ = extract_message_body(message)

        if not plain_text.strip():
            continue

        invoice = extract_invoice_data(
            plain_text,
            source_type="email_body",
            source_account=source_account,
            source_email_id=message_id,
        )

        if invoice is None:
            continue

        destination = save_invoice_body_as_pdf(
            plain_text,
            invoice,
            output_directory,
        )

        invoice.file_path = str(destination)

        invoices.append(invoice)

    return invoices

def collect_and_process_invoices(
    service,
    messages,
    download_directory,
    output_directory,
    summary_path,
    expected_vendors,
    source_account="",
):
    """Collect invoices from Gmail using the appropriate invoice source."""

    pdf_records = []
    body_messages = []

    download_directory = Path(download_directory)
    download_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    for message_summary in messages:
        message_id = message_summary["id"]

        message = get_message(
            service,
            message_id,
        )

        plain_text, html = extract_message_body(message)
        attachments = get_attachments(message)

        source = detect_invoice_source(
            attachments=attachments,
            body=f"{plain_text}\n{html}",
        )

        if source == "attachment":
            pdf_results = download_pdf_attachments(
                service=service,
                messages=[message_summary],
                download_directory=download_directory,
                source_account=source_account,
            )

            pdf_records.extend(pdf_results)

        elif source == "email_body":
            body_messages.append(message_summary)

    attachment_invoices, _ = process_invoice_records(
        records=pdf_records,
        output_directory=output_directory,
        summary_path=summary_path,
        expected_vendors=expected_vendors,
    )

    body_invoices = []

    if body_messages:
        body_invoices = process_email_body_invoices(
            service=service,
            messages=body_messages,
            output_directory=output_directory,
            source_account=source_account,
    )

    invoices = attachment_invoices + body_invoices

    write_summary_csv(
        invoices,
        summary_path,
    )

    missing_vendors = [
        vendor
        for vendor in expected_vendors
        if not any(
            invoice.vendor.casefold() == vendor.casefold()
            for invoice in invoices
        )
    ]

    return invoices, missing_vendors


def collect_invoices_for_date_range(
    service,
    start_date,
    end_date,
    download_directory,
    output_directory,
    summary_path,
    expected_vendors,
    source_account="",
):
    """Search Gmail for messages in a date range and process PDFs."""

    messages = get_messages_for_date_range(
        service,
        start_date,
        end_date,
    )

    return collect_and_process_invoices(
        service=service,
        messages=messages,
        download_directory=download_directory,
        output_directory=output_directory,
        summary_path=summary_path,
        expected_vendors=expected_vendors,
        source_account=source_account,
    )