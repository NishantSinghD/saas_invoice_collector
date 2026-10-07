import hashlib
from pathlib import Path

from src.invoices.models import InvoiceData


def calculate_file_hash(file_path):
    """Return the SHA-256 hash of a file."""

    digest = hashlib.sha256()

    with Path(file_path).open("rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            digest.update(chunk)

    return digest.hexdigest()


def invoice_identity(invoice: InvoiceData):
    """Return a stable identity tuple for an invoice."""

    return (
        invoice.vendor.strip().casefold(),
        invoice.invoice_number.strip().casefold(),
        invoice.invoice_date,
        invoice.amount,
        invoice.currency.upper(),
    )


def is_duplicate_invoice(
    invoice: InvoiceData,
    existing_invoices: list[InvoiceData],
):
    """Check whether an invoice matches an existing invoice."""

    for existing in existing_invoices:
        if (
            invoice.invoice_hash
            and existing.invoice_hash
            and invoice.invoice_hash == existing.invoice_hash
        ):
            return True

        if invoice_identity(invoice) == invoice_identity(existing):
            return True

    return False