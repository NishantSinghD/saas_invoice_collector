from datetime import date
from decimal import Decimal

from src.invoices.gaps import find_missing_vendors
from src.invoices.models import InvoiceData


def make_invoice(vendor):
    return InvoiceData(
        vendor=vendor,
        invoice_date=date(2026, 9, 15),
        amount=Decimal("125.00"),
        currency="USD",
        invoice_number=f"{vendor}-001",
        source_type="attachment",
    )


def test_finds_missing_vendors():
    expected = [
        "Slack",
        "Notion",
        "AWS",
        "GitHub",
    ]

    invoices = [
        make_invoice("Slack"),
        make_invoice("AWS"),
    ]

    missing = find_missing_vendors(
        expected,
        invoices,
    )

    assert missing == [
        "Notion",
        "GitHub",
    ]


def test_vendor_matching_is_case_insensitive():
    expected = ["Slack", "Notion"]

    invoices = [
        make_invoice("slack"),
    ]

    assert find_missing_vendors(
        expected,
        invoices,
    ) == ["Notion"]


def test_returns_empty_list_when_all_vendors_present():
    expected = ["Slack", "Notion"]

    invoices = [
        make_invoice("Slack"),
        make_invoice("Notion"),
    ]

    assert find_missing_vendors(
        expected,
        invoices,
    ) == []