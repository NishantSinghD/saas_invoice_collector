import csv
import re
from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

from src.invoices.models import InvoiceData
import csv
from pathlib import Path
import re

from src.invoices.models import InvoiceData


def sanitize_filename(value):
    """Make a string safe for use as a filename."""

    value = str(value).strip()

    return re.sub(
        r"[^A-Za-z0-9._-]+",
        "_",
        value,
    )


def build_invoice_filename(invoice: InvoiceData):
    """Build the standardized invoice filename."""

    vendor = sanitize_filename(invoice.vendor)
    amount = f"{invoice.amount:.2f}"

    return (
        f"{invoice.invoice_date.strftime('%Y-%m')}_"
        f"{vendor}_"
        f"{amount}.pdf"
    )


def save_invoice_pdf(
    source_path,
    invoice: InvoiceData,
    output_directory,
):
    """Copy an invoice PDF into the standardized output folder."""

    output_directory = Path(output_directory)
    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = build_invoice_filename(invoice)
    destination = output_directory / filename

    destination.write_bytes(
        Path(source_path).read_bytes()
    )

    return destination

def save_invoice_body_as_pdf(
    email_body,
    invoice,
    output_directory,
):
    """Create a PDF invoice from the email body."""

    output_directory = Path(output_directory)
    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = build_invoice_filename(invoice)
    destination = output_directory / filename

    pdf = canvas.Canvas(
        str(destination),
        pagesize=LETTER,
    )

    width, height = LETTER
    x = 72
    y = height - 72

    for line in email_body.splitlines():
        line = line.strip()

        if not line:
            y -= 12
            continue

        pdf.drawString(x, y, line)
        y -= 14

        if y < 72:
            pdf.showPage()
            y = height - 72

    pdf.save()

    return destination


def write_summary_csv(invoices, output_path):
    """Write processed invoices to a summary CSV file."""

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "vendor",
        "date",
        "amount",
        "currency",
        "source_account",
        "file_path",
    ]

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for invoice in invoices:
            writer.writerow(
                {
                    "vendor": invoice.vendor,
                    "date": invoice.invoice_date.isoformat(),
                    "amount": str(invoice.amount),
                    "currency": invoice.currency,
                    "source_account": invoice.source_account,
                    "file_path": invoice.file_path,
                }
            )

    return output_path