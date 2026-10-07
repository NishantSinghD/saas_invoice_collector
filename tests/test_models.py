
from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.invoices.models import InvoiceData


def test_valid_invoice_data():
    invoice = InvoiceData(
        vendor="Slack",
        invoice_date=date(2026, 9, 15),
        amount=Decimal("125.00"),
        currency="USD",
        invoice_number="SL-2026-09-001",
        source_type="attachment",
    )

    assert invoice.vendor == "Slack"
    assert invoice.amount == Decimal("125.00")
    assert invoice.currency == "USD"


def test_rejects_negative_amount():
    with pytest.raises(ValidationError):
        InvoiceData(
            vendor="Slack",
            invoice_date=date(2026, 9, 15),
            amount=Decimal("-125.00"),
            currency="USD",
            invoice_number="SL-2026-09-001",
            source_type="attachment",
        )


def test_rejects_invalid_source_type():
    with pytest.raises(ValidationError):
        InvoiceData(
            vendor="Slack",
            invoice_date=date(2026, 9, 15),
            amount=Decimal("125.00"),
            currency="USD",
            invoice_number="SL-2026-09-001",
            source_type="unknown",
        )
