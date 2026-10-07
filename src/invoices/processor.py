
from src.invoices.extractor import extract_invoice_data
from src.invoices.pdf_reader import extract_text_from_pdf


def process_invoice_pdf(
    file_path,
    source_account="",
    source_email_id="",
):
    """Extract structured invoice data from a PDF file."""

    text = extract_text_from_pdf(file_path)

    return extract_invoice_data(
        text,
        source_type="attachment",
        source_account=source_account,
        source_email_id=source_email_id,
    )
