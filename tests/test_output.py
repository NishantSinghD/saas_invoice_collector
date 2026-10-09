from datetime import date
from decimal import Decimal
from src.invoices.output import write_missing_vendors_csv
from src.invoices.models import InvoiceData
from src.invoices.output import (
    build_invoice_filename,
    sanitize_filename,
    write_summary_csv,
)
from src.invoices.output import (
    save_invoice_pdf,
    save_invoice_body_as_pdf,
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


def test_sanitize_filename():
    assert sanitize_filename("Google Workspace / India") == (
        "Google_Workspace_India"
    )


def test_build_invoice_filename():
    invoice = make_invoice()

    assert build_invoice_filename(invoice) == (
        "2026-09_Slack_125.00.pdf"
    )


def test_writes_summary_csv(tmp_path):
    invoice = make_invoice()

    invoice.file_path = (
        r"C:\Users\test\project\output\invoices\2026-09_Slack_125.00.pdf"
    )

    output_path = tmp_path / "summary.csv"

    result = write_summary_csv(
        [invoice],
        output_path,
    )

    assert result.exists()

    content = result.read_text(
        encoding="utf-8"
    )

    assert (
        "vendor,date,amount,currency,source_account,"
        "source_type,file_link"
    ) in content

    assert (
        "Slack,2026-09-15,125.00,USD,,attachment,"
        in content
    )

    assert (
        "output/invoices/2026-09_Slack_125.00.pdf"
        in content
    )
def test_writes_missing_vendors_csv(tmp_path):
    output_path = tmp_path / "missing_vendors.csv"

    result = write_missing_vendors_csv(
        ["Notion", "AWS"],
        output_path,
    )

    assert result.exists()

    content = result.read_text(
        encoding="utf-8"
    )

    assert content == (
        "vendor,status\n"
        "Notion,MISSING\n"
        "AWS,MISSING\n"
    )

def test_save_invoice_pdf_does_not_overwrite_existing_file(tmp_path):
    source_one = tmp_path / "source_one.pdf"
    source_two = tmp_path / "source_two.pdf"
    output_dir = tmp_path / "invoices"

    source_one.write_bytes(b"first invoice PDF")
    source_two.write_bytes(b"second invoice PDF")

    invoice = make_invoice()

    first = save_invoice_pdf(source_one, invoice, output_dir)
    second = save_invoice_pdf(source_two, invoice, output_dir)

    assert first.name == "2026-09_Slack_125.00.pdf"
    assert second.name == "2026-09_Slack_125.00_2.pdf"
    assert first.read_bytes() == b"first invoice PDF"
    assert second.read_bytes() == b"second invoice PDF"


def test_save_invoice_body_as_pdf_does_not_overwrite_existing_file(tmp_path):
    output_dir = tmp_path / "invoices"
    invoice = make_invoice()

    first = save_invoice_body_as_pdf(
        "First invoice",
        invoice,
        output_dir,
    )
    first_content = first.read_bytes()

    second = save_invoice_body_as_pdf(
        "Second invoice",
        invoice,
        output_dir,
    )

    assert first.name == "2026-09_Slack_125.00.pdf"
    assert second.name == "2026-09_Slack_125.00_2.pdf"
    assert first.read_bytes() == first_content
    assert first.read_bytes() != second.read_bytes()
