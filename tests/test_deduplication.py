
from datetime import date
from decimal import Decimal

from src.invoices.deduplication import (
    calculate_file_hash,
    is_duplicate_invoice,
)
from src.invoices.models import InvoiceData


def make_invoice(invoice_number="SL-001", invoice_hash=""):
    return InvoiceData(
        vendor="Slack",
        invoice_date=date(2026, 9, 15),
        amount=Decimal("125.00"),
        currency="USD",
        invoice_number=invoice_number,
        source_type="attachment",
        invoice_hash=invoice_hash,
    )


def test_identical_files_have_same_hash(tmp_path):
    first = tmp_path / "first.pdf"
    second = tmp_path / "second.pdf"

    first.write_bytes(b"same invoice content")
    second.write_bytes(b"same invoice content")

    assert calculate_file_hash(first) == calculate_file_hash(second)


def test_detects_duplicate_by_invoice_identity():
    first = make_invoice()
    second = make_invoice()

    assert is_duplicate_invoice(second, [first]) is True


def test_does_not_flag_different_invoice_numbers():
    first = make_invoice(invoice_number="SL-001")
    second = make_invoice(invoice_number="SL-002")

    assert is_duplicate_invoice(second, [first]) is False


def test_detects_duplicate_by_hash():
    first = make_invoice(invoice_hash="abc123")
    second = make_invoice(
        invoice_number="SL-999",
        invoice_hash="abc123",
    )

    assert is_duplicate_invoice(second, [first]) is True
