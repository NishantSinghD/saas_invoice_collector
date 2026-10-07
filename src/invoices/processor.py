from src.invoices.extractor import extract_invoice_data
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

    return extract_invoice_data(
        combined_text,
        source_type="attachment",
        source_account=source_account,
        source_email_id=source_email_id,
    )