import re
from datetime import datetime
from decimal import Decimal

from src.invoices.models import InvoiceData


def extract_invoice_data(
    text,
    source_type="email_body",
    source_account="",
    source_email_id="",
):
    """Extract basic invoice fields from predictable invoice text."""

    def find_value(pattern):
        match = re.search(
            pattern,
            text,
            re.IGNORECASE | re.MULTILINE,
        )
        return match.group(1).strip() if match else None

    vendor = find_value(
        r"^\s*Vendor:\s*(.+?)\s*$"
    )

    invoice_date_text = find_value(
        r"^\s*Invoice Date:\s*(.+?)\s*$"
    )

    invoice_number = find_value(
        r"^\s*Invoice\s+Number:\s*(.+?)\s*$"
    )

    amount_match = re.search(
        r"^\s*(?:Amount|Amount Due|Total Due|Total):\s*"
        r"(?:(USD|INR|EUR|GBP)\s*)?"
        r"([0-9,]+(?:\.[0-9]{1,2})?)"
        r"(?:\s*(USD|INR|EUR|GBP))?\s*$",
        text,
        re.IGNORECASE | re.MULTILINE,
    )

    if not all(
        [
            vendor,
            invoice_date_text,
            invoice_number,
            amount_match,
        ]
    ):
        return None

    try:
        invoice_date = datetime.strptime(
            invoice_date_text,
            "%B %d, %Y",
        ).date()

    except ValueError:
        try:
            invoice_date = datetime.strptime(
                invoice_date_text,
                "%Y-%m-%d",
            ).date()

        except ValueError:
            return None

    currency = (
        amount_match.group(1)
        or amount_match.group(3)
        or ""
    ).upper()

    if not currency:
        return None

    amount = Decimal(
        amount_match.group(2).replace(",", "")
    )

    return InvoiceData(
        vendor=vendor,
        invoice_date=invoice_date,
        amount=amount,
        currency=currency,
        invoice_number=invoice_number,
        source_type=source_type,
        source_account=source_account,
        source_email_id=source_email_id,
    )