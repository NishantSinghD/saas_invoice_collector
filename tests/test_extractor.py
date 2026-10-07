
from datetime import date
from decimal import Decimal

from src.invoices.extractor import extract_invoice_data


def test_extracts_slack_invoice_from_email_body():
    text = """
    Vendor: Slack
    Invoice Date: September 15, 2026
    Invoice Number: SL-2026-09-001
    Amount: USD 125.00
    """

    invoice = extract_invoice_data(
        text,
        source_type="email_body",
        source_account="finance-test@example.com",
        source_email_id="message-123",
    )

    assert invoice is not None
    assert invoice.vendor == "Slack"
    assert invoice.invoice_date == date(2026, 9, 15)
    assert invoice.amount == Decimal("125.00")
    assert invoice.currency == "USD"
    assert invoice.invoice_number == "SL-2026-09-001"
    assert invoice.source_account == "finance-test@example.com"


def test_returns_none_when_required_fields_are_missing():
    text = """
    Vendor: Slack
    Amount: USD 125.00
    """

    assert extract_invoice_data(text) is None


def test_extracts_amount_with_comma_separator():
    text = """
    Vendor: AWS
    Invoice Date: September 15, 2026
    Invoice Number: AWS-2026-09
    Amount Due: USD 1,250.50
    """

    invoice = extract_invoice_data(text)

    assert invoice is not None
    assert invoice.amount == Decimal("1250.50")
