from pathlib import Path

from src.invoices.deduplication import calculate_file_hash
from src.invoices.gaps import find_missing_vendors
from src.invoices.output import (
    save_invoice_pdf,
    write_summary_csv,
)
from src.invoices.processor import process_invoice_pdf


def process_pdf_invoices(
    pdf_files,
    output_directory,
    summary_path,
    expected_vendors,
    source_account="",
    source_email_id="",
):
    """Process local PDF invoices into standardized outputs."""

    records = [
        {
            "file_path": Path(pdf_file),
            "source_account": source_account,
            "source_email_id": source_email_id,
        }
        for pdf_file in pdf_files
    ]

    return process_invoice_records(
        records,
        output_directory,
        summary_path,
        expected_vendors,
    )


def process_invoice_records(
    records,
    output_directory,
    summary_path,
    expected_vendors,
):
    """Process PDF records while preserving per-email metadata."""

    invoices = []
    seen_hashes = set()
    seen_identities = set()

    for record in records:
        pdf_file = Path(record["file_path"])
        file_hash = calculate_file_hash(pdf_file)

        if file_hash in seen_hashes:
            continue

        invoice = process_invoice_pdf(
            pdf_file,
            source_account=record.get("source_account", ""),
            source_email_id=record.get("source_email_id", ""),
            email_body=record.get("email_body", ""),
        )

        if invoice is None:
            continue

        invoice_identity = (
            invoice.vendor.strip().casefold(),
            invoice.invoice_number.strip().casefold(),
            invoice.invoice_date,
            invoice.amount,
            invoice.currency.upper(),
        )

        if invoice_identity in seen_identities:
            continue

        seen_hashes.add(file_hash)
        seen_identities.add(invoice_identity)

        invoice.invoice_hash = file_hash

        destination = save_invoice_pdf(
            pdf_file,
            invoice,
            output_directory,
        )

        invoice.file_path = str(destination)
        invoices.append(invoice)

    write_summary_csv(invoices, summary_path)

    missing_vendors = find_missing_vendors(
        expected_vendors,
        invoices,
    )

    return invoices, missing_vendors