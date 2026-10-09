
import csv
import re
from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

from src.invoices.models import InvoiceData


def sanitize_filename(value):
    """Make a string safe for use as a filename."""
    value = str(value).strip()
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value)


def build_invoice_filename(invoice: InvoiceData):
    """Build the standardized invoice filename."""
    vendor = sanitize_filename(invoice.vendor)
    amount = f"{invoice.amount:.2f}"

    return (
        f"{invoice.invoice_date.strftime('%Y-%m')}_"
        f"{vendor}_"
        f"{amount}.pdf"
    )


def get_unique_destination(output_directory, filename):
    """Return a filename that will not overwrite an existing file."""
    output_directory = Path(output_directory)
    destination = output_directory / filename

    if not destination.exists():
        return destination

    stem = destination.stem
    suffix = destination.suffix
    counter = 2

    while True:
        candidate = output_directory / f"{stem}_{counter}{suffix}"

        if not candidate.exists():
            return candidate

        counter += 1


def save_invoice_pdf(source_path, invoice: InvoiceData, output_directory):
    """Copy an invoice PDF without overwriting another invoice."""
    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)

    filename = build_invoice_filename(invoice)
    destination = get_unique_destination(output_directory, filename)

    destination.write_bytes(Path(source_path).read_bytes())

    return destination


def save_invoice_body_as_pdf(email_body, invoice, output_directory):
    """Create a PDF invoice from the email body without overwriting files."""
    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)

    filename = build_invoice_filename(invoice)
    destination = get_unique_destination(output_directory, filename)

    pdf = canvas.Canvas(str(destination), pagesize=LETTER)

    _, height = LETTER
    x = 72
    y = height - 72

    for line in email_body.splitlines():
        line = line.strip()

        if not line:
            y -= 12
            continue

        if y < 72:
            pdf.showPage()
            y = height - 72

        pdf.drawString(x, y, line)
        y -= 14

    pdf.save()

    return destination


def write_summary_csv(invoices, output_path):
    """Write processed invoices to a summary CSV file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "vendor",
        "date",
        "amount",
        "currency",
        "source_account",
        "source_type",
        "file_link",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for invoice in invoices:
            writer.writerow(
                {
                    "vendor": invoice.vendor,
                    "date": invoice.invoice_date.isoformat(),
                    "amount": str(invoice.amount),
                    "currency": invoice.currency,
                    "source_account": invoice.source_account,
                    "source_type": invoice.source_type,
                    "file_link": Path(invoice.file_path).as_posix(),
                }
            )

    return output_path


def write_combined_summary_csv(invoices, output_path):
    """Write all account invoices to one consolidated CSV file."""
    return write_summary_csv(invoices, output_path)


def write_missing_vendors_csv(missing_vendors, output_path):
    """Write missing expected vendors to a CSV report."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["vendor", "status"])

        for vendor in missing_vendors:
            writer.writerow([vendor, "MISSING"])

    return output_path
