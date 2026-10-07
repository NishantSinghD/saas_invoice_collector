
from reportlab.pdfgen import canvas

from src.invoices.pdf_reader import extract_text_from_pdf


def test_extracts_text_from_pdf(tmp_path):
    pdf_path = tmp_path / "sample_invoice.pdf"

    pdf = canvas.Canvas(str(pdf_path))
    pdf.drawString(72, 750, "Invoice Number: SL-2026-09-001")
    pdf.drawString(72, 730, "Amount Due: USD 125.00")
    pdf.save()

    text = extract_text_from_pdf(pdf_path)

    assert "Invoice Number: SL-2026-09-001" in text
    assert "Amount Due: USD 125.00" in text


def test_raises_error_for_missing_pdf(tmp_path):
    missing_path = tmp_path / "missing.pdf"

    try:
        extract_text_from_pdf(missing_path)
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("Expected FileNotFoundError")


def test_rejects_non_pdf_file(tmp_path):
    text_path = tmp_path / "sample.txt"
    text_path.write_text("This is not a PDF.")

    try:
        extract_text_from_pdf(text_path)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")
