
from src.gmail.client import (
    download_attachment,
    get_message,
    get_messages_for_date_range,
)
import re
from pathlib import Path

from src.gmail.client import download_attachment, get_message
from src.gmail.parser import get_attachments
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
                }
            )

    return downloaded_files


def collect_and_process_invoices(
    service,
    messages,
    download_directory,
    output_directory,
    summary_path,
    expected_vendors,
    source_account="",
):
    """Download Gmail PDF attachments and process the invoices."""

    records = download_pdf_attachments(
        service=service,
        messages=messages,
        download_directory=download_directory,
        source_account=source_account,
    )

    invoices, missing_vendors = process_invoice_records(
        records=records,
        output_directory=output_directory,
        summary_path=summary_path,
        expected_vendors=expected_vendors,
    )

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
