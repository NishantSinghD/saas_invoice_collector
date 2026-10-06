from src.invoices.detector import is_likely_invoice_email


def test_detects_invoice_keyword_in_subject():
    assert is_likely_invoice_email(
        subject="Your September invoice",
        sender="billing@example.com",
    )


def test_detects_billing_keyword_in_body():
    assert is_likely_invoice_email(
        subject="Your account statement",
        sender="billing@example.com",
        body="Your monthly billing statement is attached.",
    )


def test_rejects_unrelated_email():
    assert not is_likely_invoice_email(
        subject="Your account is live",
        sender="google@example.com",
        body="Finish setting up your account.",
    )