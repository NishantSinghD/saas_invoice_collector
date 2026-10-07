
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class InvoiceData(BaseModel):
    """Structured data extracted from an invoice."""

    vendor: str = Field(min_length=1)
    invoice_date: date
    amount: Decimal = Field(ge=0)
    currency: str = Field(min_length=3, max_length=3)
    invoice_number: str = Field(min_length=1)

    source_account: str = ""
    source_email_id: str = ""
    source_type: Literal[
        "attachment",
        "billing_portal",
        "email_body",
    ]

    file_path: str = ""
    invoice_hash: str = ""
    processing_status: str = "extracted"
