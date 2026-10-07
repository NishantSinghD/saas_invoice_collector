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
    """Process a collection of PDF invoices."""

    invoices = []
    seen_hashes = set()

    for pdf_file in pdf_files:
        pdf_file = Path(pdf_file)

        file_hash = calculate_file_hash(pdf_file)

        if file_hash in seen_hashes:
            continue

        seen_hashes.add(file_hash)

        invoice = process_invoice_pdf(
    pdf_file,
    source_account=source_account,
    source_email_id=source_email_id,
)

        if invoice is None:
            continue

        invoice.invoice_hash = file_hash

        destination = save_invoice_pdf(
            pdf_file,
            invoice,
            output_directory,
        )

        invoice.file_path = str(destination)

        invoices.append(invoice)

    write_summary_csv(
        invoices,
        summary_path,
    )

    missing_vendors = find_missing_vendors(
        expected_vendors,
        invoices,
    )

    return invoices, missing_vendors