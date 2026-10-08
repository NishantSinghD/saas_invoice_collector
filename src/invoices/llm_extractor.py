import json
import re
from datetime import date
from decimal import Decimal

import httpx
from pydantic import BaseModel, ValidationError


OLLAMA_URL = "http://127.0.0.1:11434/api/chat"


class LLMInvoiceData(BaseModel):
    vendor: str
    invoice_date: str
    amount: str
    currency: str
    invoice_number: str

    @property
    def normalized_amount(self):
        match = re.fullmatch(
            r"\s*(?:[A-Za-z]+\s*)?([0-9,]+(?:\.[0-9]{1,2})?)\s*",
            self.amount,
        )

        if not match:
            raise ValueError(
                f"LLM did not return a usable numeric amount: {self.amount}"
            )

        return match.group(1).replace(",", "")


INVOICE_SCHEMA = {
    "type": "object",
    "properties": {
        "vendor": {"type": "string"},
        "invoice_date": {"type": "string"},
        "amount": {"type": "string"},
        "currency": {"type": "string"},
        "invoice_number": {"type": "string"},
    },
    "required": [
        "vendor",
        "invoice_date",
        "amount",
        "currency",
        "invoice_number",
    ],
}


def extract_invoice_data_with_ollama(
    text,
    model="qwen2.5:3b",
):
    """Extract invoice fields using a local Ollama model."""

    prompt = f"""
Extract the invoice information from the text below.

Rules:
- vendor: company that issued the invoice.
- invoice_date: use YYYY-MM-DD.
- amount: copy only the numeric value associated with the invoice's
  total, balance payable, amount due, or total due.
- amount must contain ONLY digits and an optional decimal point.
- For example, if the invoice says "Balance payable: USD 125.00",
  return "125.00".
- Never return explanatory text in the amount field.
- currency: three-letter currency code such as USD, EUR, GBP, or INR.
- invoice_number: invoice or statement number.
- If the invoice contains "Balance payable", use that value as the amount.

Do not invent information.

Invoice text:
{text}
"""

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "stream": False,
        "format": INVOICE_SCHEMA,
    }

    response = httpx.post(
        OLLAMA_URL,
        json=payload,
        timeout=120,
    )
    response.raise_for_status()

    response_data = response.json()
    raw_output = response_data["message"]["content"].strip()

    try:
        data = json.loads(raw_output)
        return LLMInvoiceData.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as error:
        raise ValueError(
            f"Ollama returned invalid invoice data: {raw_output}"
        ) from error


def convert_llm_invoice_to_invoice_data(
    llm_invoice,
    source_type,
    source_account="",
    source_email_id="",
):
    """Convert validated LLM output into the application's InvoiceData model."""

    from src.invoices.models import InvoiceData

    try:
        invoice_date = date.fromisoformat(llm_invoice.invoice_date)
        amount = Decimal(llm_invoice.normalized_amount)

        return InvoiceData(
            vendor=llm_invoice.vendor,
            invoice_date=invoice_date,
            amount=amount,
            currency=llm_invoice.currency.upper(),
            invoice_number=llm_invoice.invoice_number,
            source_type=source_type,
            source_account=source_account,
            source_email_id=source_email_id,
        )
    except (ValueError, ArithmeticError) as error:
        raise ValueError(
            f"Could not convert LLM invoice data: {llm_invoice}"
        ) from error