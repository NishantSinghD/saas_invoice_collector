
from reportlab.pdfgen import canvas

from src.invoices.processor import process_invoice_pdf


def test_process_invoice_pdf(tmp_path):
    pdf_path = tmp_path / "slack_invoice.pdf"

    pdf = canvas.Canvas(str(pdf_path))
    pdf.drawString(72, 750, "Vendor: Slack")
    pdf.drawString(72, 730, "Invoice Date: September 15, 2026")
    pdf.drawString(72, 710, "Invoice Number: SL-2026-09-001")
    pdf.drawString(72, 690, "Amount Due: USD 125.00")
    pdf.save()

    invoice = process_invoice_pdf(
        pdf_path,
        source_account="finance-test@example.com",
        source_email_id="message-123",
    )

    assert invoice is not None
    assert invoice.vendor == "Slack"
    assert invoice.amount == 125
    assert invoice.currency == "USD"
    assert invoice.invoice_number == "SL-2026-09-001"
    assert invoice.source_type == "attachment"
    assert invoice.source_account == "finance-test@example.com"
    assert invoice.source_email_id == "message-123"
