INVOICE_KEYWORDS = {
    "invoice",
    "receipt",
    "billing",
    "bill",
    "payment",
    "statement",
}


def is_likely_invoice_email(subject, sender, body=""):
    """
    Determine whether an email is likely to contain an invoice.

    This is a lightweight first-pass filter. It is intentionally
    conservative and does not make the final invoice decision.
    """

    text = " ".join(
        [
            subject or "",
            sender or "",
            body or "",
        ]
    ).lower()

    return any(
        keyword in text
        for keyword in INVOICE_KEYWORDS
    )