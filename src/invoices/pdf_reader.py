
from pathlib import Path

import pymupdf


def extract_text_from_pdf(file_path):
    """Extract selectable text from a PDF file."""

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("The supplied file must be a PDF.")

    text_parts = []

    with pymupdf.open(path) as document:
        for page in document:
            text_parts.append(page.get_text())

    return "\n".join(text_parts).strip()
