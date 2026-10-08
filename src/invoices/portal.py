import httpx
from urllib.parse import urlparse


def extract_urls(text):
    """Extract HTTP(S) URLs from text."""

    import re

    return re.findall(
        r"https?://[^\s<>\"]+",
        text,
    )


def is_safe_http_url(url):
    """Return True when the URL uses HTTP(S) and has a hostname."""

    parsed = urlparse(url)

    return (
        parsed.scheme in {"http", "https"}
        and bool(parsed.netloc)
    )


def find_billing_portal_url(text):
    """Find the first invoice/billing-related URL."""

    for url in extract_urls(text):
        clean_url = url.rstrip(".,);]")

        if not is_safe_http_url(clean_url):
            continue

        lowered = clean_url.casefold()

        if any(
            keyword in lowered
            for keyword in (
                "invoice",
                "billing",
                "receipt",
            )
        ):
            return clean_url

    return None


def download_portal_pdf(
    url,
    destination,
):
    """Download a PDF directly from a billing URL."""

    if not is_safe_http_url(url):
        raise ValueError("Unsafe or invalid URL.")

    destination = str(destination)

    response = httpx.get(
        url,
        follow_redirects=True,
        timeout=30,
    )

    response.raise_for_status()

    content_type = response.headers.get(
        "content-type",
        "",
    ).casefold()

    if "application/pdf" not in content_type:
        raise ValueError(
            "Billing portal URL did not return a PDF."
        )

    with open(destination, "wb") as file:
        file.write(response.content)

    return destination