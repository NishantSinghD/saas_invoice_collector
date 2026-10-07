from src.invoices.source_detector import detect_invoice_source


def test_detects_pdf_attachment():
    attachments = [
        {
            "filename": "invoice.pdf",
            "mime_type": "application/pdf",
        }
    ]

    assert detect_invoice_source(
        attachments,
        "Your invoice is attached.",
    ) == "attachment"


def test_detects_billing_portal():
    assert detect_invoice_source(
        [],
        "View your invoice at https://billing.example.com/invoices/123",
    ) == "billing_portal"


def test_detects_invoice_in_body():
    assert detect_invoice_source(
        [],
        """
        Invoice Number: INV-123
        Invoice Date: September 15, 2026
        Amount Due: USD 125.00
        """,
    ) == "email_body"


def test_returns_none_for_unrelated_email():
    assert detect_invoice_source(
        [],
        "Thanks for using our product. Have a great day!",
    ) is None