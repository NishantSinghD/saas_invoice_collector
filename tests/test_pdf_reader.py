from pathlib import Path

import pytest

from src.invoices.pdf_reader import extract_text_from_pdf


def test_extract_text_from_pdf(tmp_path):
    pdf_path = tmp_path / "invoice.pdf"

    import fitz

    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "Invoice Number: INV-001")
    document.save(pdf_path)
    document.close()

    text = extract_text_from_pdf(pdf_path)

    assert "Invoice Number: INV-001" in text


def test_extract_text_from_pdf_file_not_found():
    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf(
            Path("does_not_exist.pdf")
        )


def test_extract_text_from_pdf_rejects_non_pdf(tmp_path):
    text_file = tmp_path / "invoice.txt"
    text_file.write_text("This is not a PDF.")

    with pytest.raises(ValueError, match="must be a PDF"):
        extract_text_from_pdf(text_file)