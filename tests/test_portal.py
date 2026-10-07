from src.invoices.portal import (
    find_billing_portal_url,
    is_safe_http_url,
)

def test_finds_billing_portal_url():
    body = (
        "Your invoice is available at "
        "https://billing.example.com/invoices/12345"
    )

    assert (
        find_billing_portal_url(body)
        == "https://billing.example.com/invoices/12345"
    )


def test_ignores_unrelated_url():
    body = (
        "Learn more at "
        "https://example.com/about"
    )

    assert find_billing_portal_url(body) is None

def test_rejects_non_http_url():
    assert not is_safe_http_url(
        "file:///etc/passwd"
    )