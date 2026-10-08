from src.invoices.extractor import extract_invoice_data
from src.invoices.llm_extractor import (
    convert_llm_invoice_to_invoice_data,
    extract_invoice_data_with_ollama,
)
from src.invoices.pdf_reader import extract_text_from_pdf


def process_invoice_pdf(
    file_path,
    source_account="",
    source_email_id="",
    email_body="",
):
    """Extract structured invoice data from a PDF file."""

    pdf_text = extract_text_from_pdf(file_path)

    combined_text = pdf_text
    if email_body.strip():
        combined_text = f"{email_body}\n{pdf_text}"

    # First attempt: deterministic extraction.
    invoice = extract_invoice_data(
        combined_text,
        source_type="attachment",
        source_account=source_account,
        source_email_id=source_email_id,
    )

    if invoice is not None:
        return invoice

    # Fallback: local LLM for ambiguous invoices.
    llm_invoice = extract_invoice_data_with_ollama(
        combined_text,
    )

    return convert_llm_invoice_to_invoice_data(
        llm_invoice,
        source_type="attachment",
        source_account=source_account,
        source_email_id=source_email_id,
    )