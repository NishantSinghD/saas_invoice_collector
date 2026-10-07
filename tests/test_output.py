from src.invoices.output import write_summary_csv
from datetime import date
from decimal import Decimal

from src.invoices.models import InvoiceData
from src.invoices.output import (
    build_invoice_filename,
    sanitize_filename,
    save_invoice_body_as_pdf,
    save_invoice_pdf,
)


def make_invoice():
    return InvoiceData(
        vendor="Slack",
        invoice_date=date(2026, 9, 15),
        amount=Decimal("125.00"),
        currency="USD",
        invoice_number="SL-2026-09-001",
        source_type="attachment",
    )


def test_builds_invoice_filename():
    invoice = make_invoice()

    assert build_invoice_filename(invoice) == (
        "2026-09_Slack_125.00.pdf"
    )


def test_sanitizes_filename():
    assert sanitize_filename("Google Workspace / India") == (
        "Google_Workspace_India"
    )


def test_saves_invoice_pdf(tmp_path):
    source = tmp_path / "original.pdf"
    source.write_bytes(b"fake pdf content")

    output_directory = tmp_path / "invoices"

    invoice = make_invoice()

    destination = save_invoice_pdf(
        source,
        invoice,
        output_directory,
    )

    assert destination.name == "2026-09_Slack_125.00.pdf"
    assert destination.exists()
    assert destination.read_bytes() == b"fake pdf content"
def test_writes_summary_csv(tmp_path):
    invoice = make_invoice()
    invoice.file_path = "output/invoices/2026-09_Slack_125.00.pdf"

    output_path = tmp_path / "summary.csv"

    result = write_summary_csv(
        [invoice],
        output_path,
    )

    assert result.exists()

    content = result.read_text(encoding="utf-8")

    assert "vendor,date,amount,currency,source_account,file_path" in content
    assert "Slack" in content
    assert "2026-09-15" in content
    assert "125.00" in content
    assert "USD" in content
    assert "output/invoices/2026-09_Slack_125.00.pdf" in content

def test_saves_invoice_body_as_pdf(tmp_path):
    invoice = make_invoice()

    email_body = """Your September 2026 invoice is attached.

Vendor: Slack
Invoice Date: September 15, 2026
Invoice Number: SL-2026-09-001
Amount: USD 125.00
"""

    output_directory = tmp_path / "invoices"

    destination = save_invoice_body_as_pdf(
        email_body,
        invoice,
        output_directory,
    )

    assert destination.name == "2026-09_Slack_125.00.pdf"
    assert destination.exists()
    assert destination.stat().st_size > 0