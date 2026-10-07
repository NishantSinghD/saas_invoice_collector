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

def test_download_portal_pdf(tmp_path, monkeypatch):
    destination = tmp_path / "invoice.pdf"

    class FakeResponse:
        headers = {
            "content-type": "application/pdf",
        }
        content = b"%PDF-1.4 fake invoice"

        def raise_for_status(self):
            pass

    monkeypatch.setattr(
        "src.invoices.portal.httpx.get",
        lambda *args, **kwargs: FakeResponse(),
    )

    from src.invoices.portal import download_portal_pdf

    result = download_portal_pdf(
        "https://billing.example.com/invoices/123",
        destination,
    )

    assert result == str(destination)
    assert destination.exists()
    assert destination.read_bytes() == b"%PDF-1.4 fake invoice"