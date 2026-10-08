import re
from pathlib import Path

from src.invoices.source_detector import detect_invoice_source
from src.gmail.client import (
    download_attachment,
    get_message,
    get_messages_for_date_range,
)
from src.invoices.portal import (
    download_portal_pdf,
    find_billing_portal_url,
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


def is_invoice_in_date_range(invoice, start_date, end_date):
    """Return True when the invoice date falls within the requested range."""

    if invoice is None:
        return False

    return start_date <= invoice.invoice_date <= end_date


def download_pdf_attachments(
    service,
    messages,
    download_directory,
    source_account="",
):
    """Download PDF attachments and retain their email metadata."""

    download_directory = Path(download_directory)
    download_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    downloaded_files = []

    for message_summary in messages:
        message_id = message_summary["id"]

        message = get_message(
            service,
            message_id,
        )

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


def process_billing_portal_invoice(
    service,
    message,
    output_directory,
    download_directory,
    source_account="",
):
    """Download and process an invoice from a billing portal URL."""

    message_id = message["id"]

    full_message = get_message(
        service,
        message_id,
    )

    plain_text, html = extract_message_body(
        full_message
    )

    portal_url = find_billing_portal_url(
        f"{plain_text}\n{html}"
    )

    if not portal_url:
        return None

    download_directory = Path(download_directory)

    download_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    portal_filename = (
        f"{message_id}_portal_invoice.pdf"
    )

    downloaded_path = (
        download_directory / portal_filename
    )

    try:
        download_portal_pdf(
            portal_url,
            downloaded_path,
        )
    except (ValueError, OSError) as error:
        print(
            f"Portal invoice could not be downloaded "
            f"for message {message_id}: {error}"
        )
        return None

    invoice = process_invoice_pdf(
        downloaded_path,
        source_account=source_account,
        source_email_id=message_id,
        email_body=plain_text,
    )

    if invoice is None:
        return None

    destination = save_invoice_pdf(
        downloaded_path,
        invoice,
        output_directory,
    )

    invoice.file_path = str(destination)

    return invoice

def process_invoice_pdf(
    file_path,
    source_account="",
    source_email_id="",
    email_body="",
):
    """Extract structured invoice data from a PDF."""

    from src.invoices.processor import process_invoice_pdf as process_pdf

    return process_pdf(
        file_path,
        source_account=source_account,
        source_email_id=source_email_id,
        email_body=email_body,
    )


def collect_and_process_invoices(
    service,
    messages,
    download_directory,
    output_directory,
    summary_path,
    expected_vendors,
    source_account="",
    start_date=None,
    end_date=None,
):
    """Collect invoices from Gmail using the appropriate invoice source."""

    pdf_records = []
    body_messages = []
    portal_invoices = []

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

        plain_text, html = extract_message_body(
            message
        )

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

        elif source == "billing_portal":
            portal_invoice = process_billing_portal_invoice(
                service=service,
                message=message_summary,
                output_directory=output_directory,
                download_directory=download_directory,
                source_account=source_account,
            )

            if portal_invoice is not None:
                portal_invoices.append(
                    portal_invoice
                )

        elif source == "email_body":
            body_messages.append(
                message_summary
            )

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

    invoices = (
        attachment_invoices
        + portal_invoices
        + body_invoices
    )

    if start_date is not None and end_date is not None:
        invoices = [
            invoice
            for invoice in invoices
            if is_invoice_in_date_range(
                invoice,
                start_date,
                end_date,
            )
        ]

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
    """Search Gmail for messages in a date range and process invoices."""

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
        start_date=start_date,
        end_date=end_date,
    )