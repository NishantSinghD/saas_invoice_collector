from reportlab.pdfgen import canvas

from src.pipeline import process_pdf_invoices


def create_invoice_pdf(
    path,
    vendor,
    invoice_date,
    invoice_number,
    amount,
):
    pdf = canvas.Canvas(str(path))

    pdf.drawString(72, 750, f"Vendor: {vendor}")
    pdf.drawString(72, 730, f"Invoice Date: {invoice_date}")
    pdf.drawString(72, 710, f"Invoice Number: {invoice_number}")
    pdf.drawString(72, 690, f"Amount Due: USD {amount}")

    pdf.save()


def test_process_pdf_invoices(tmp_path):
    pdf_directory = tmp_path / "input"
    output_directory = tmp_path / "output"
    summary_path = tmp_path / "summary.csv"

    pdf_directory.mkdir()

    first_pdf = pdf_directory / "slack.pdf"
    second_pdf = pdf_directory / "notion.pdf"

    create_invoice_pdf(
        first_pdf,
        "Slack",
        "September 15, 2026",
        "SL-2026-09-001",
        "125.00",
    )

    create_invoice_pdf(
        second_pdf,
        "Notion",
        "September 18, 2026",
        "NOT-2026-09-001",
        "50.00",
    )

    invoices, missing = process_pdf_invoices(
        pdf_files=[first_pdf, second_pdf],
        output_directory=output_directory,
        summary_path=summary_path,
        expected_vendors=[
            "Slack",
            "Notion",
            "AWS",
        ],
        source_account="finance-test@example.com",
    )

    assert len(invoices) == 2

    assert missing == ["AWS"]

    assert (
        output_directory / "2026-09_Slack_125.00.pdf"
    ).exists()

    assert (
        output_directory / "2026-09_Notion_50.00.pdf"
    ).exists()

    assert summary_path.exists()

    summary = summary_path.read_text(
        encoding="utf-8"
    )

    assert "Slack" in summary
    assert "Notion" in summary
    assert "125.00" in summary
    assert "50.00" in summary


def test_pipeline_skips_duplicate_pdf(tmp_path):
    pdf_directory = tmp_path / "input"
    output_directory = tmp_path / "output"
    summary_path = tmp_path / "summary.csv"

    pdf_directory.mkdir()

    first_pdf = pdf_directory / "invoice1.pdf"
    duplicate_pdf = pdf_directory / "invoice2.pdf"

    create_invoice_pdf(
        first_pdf,
        "Slack",
        "September 15, 2026",
        "SL-2026-09-001",
        "125.00",
    )

    duplicate_pdf.write_bytes(
        first_pdf.read_bytes()
    )

    invoices, missing = process_pdf_invoices(
        pdf_files=[
            first_pdf,
            duplicate_pdf,
        ],
        output_directory=output_directory,
        summary_path=summary_path,
        expected_vendors=["Slack"],
    )

    assert len(invoices) == 1
    assert missing == []