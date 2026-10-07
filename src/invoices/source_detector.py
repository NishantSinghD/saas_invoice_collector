import re


PORTAL_KEYWORDS = {
    "billing",
    "invoice",
    "payment",
    "statement",
    "receipt",
}


def detect_invoice_source(attachments, body):
    """
    Determine how an invoice is represented in an email.

    Returns:
        "attachment"
        "billing_portal"
        "email_body"
        None
    """

    if _has_pdf_attachment(attachments):
        return "attachment"

    if _has_billing_portal_link(body):
        return "billing_portal"

    if _contains_invoice_information(body):
        return "email_body"

    return None


def _has_pdf_attachment(attachments):
    """Return True when the email contains a PDF attachment."""

    return any(
        attachment.get("mime_type") == "application/pdf"
        or attachment.get("filename", "").lower().endswith(".pdf")
        for attachment in attachments
    )


def _has_billing_portal_link(body):
    """Return True when the body contains a likely billing URL."""

    urls = re.findall(
        r"https?://[^\s<>\"']+",
        body or "",
    )

    return any(
        any(
            keyword in url.lower()
            for keyword in PORTAL_KEYWORDS
        )
        for url in urls
    )


def _contains_invoice_information(body):
    """Return True when the body contains basic invoice signals."""

    text = (body or "").lower()

    invoice_signals = [
        "invoice number",
        "invoice date",
        "amount due",
        "total due",
        "amount:",
        "total:",
    ]

    return any(
        signal in text
        for signal in invoice_signals
    )