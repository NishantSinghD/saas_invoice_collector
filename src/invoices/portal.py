import re
from urllib.parse import urlparse


BILLING_KEYWORDS = {
    "billing",
    "invoice",
    "payment",
    "statement",
    "receipt",
}


def extract_urls(text):
    """Extract HTTP and HTTPS URLs from text."""

    return re.findall(
        r"https?://[^\s<>\"']+",
        text or "",
    )


def find_billing_portal_url(text):
    """
    Return the first URL that appears to be a billing portal URL.
    """

    urls = extract_urls(text)

    for url in urls:
        parsed = urlparse(url)

        if parsed.scheme not in {"http", "https"}:
            continue

        if any(
            keyword in url.lower()
            for keyword in BILLING_KEYWORDS
        ):
            return url

    return None


def is_safe_http_url(url):
    """Return True only for valid HTTP(S) URLs."""

    if not url:
        return False

    parsed = urlparse(url)

    return parsed.scheme in {"http", "https"} and bool(
        parsed.netloc
    )