from datetime import date
from decimal import Decimal
from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas


BASE_DIR = Path(__file__).resolve().parents[1]

TEST_DATA_DIR = BASE_DIR / "sample_data" / "synthetic_invoices"


VENDORS = [
    "Slack",
    "Notion",
    "AWS",
    "Google Workspace",
    "GitHub",
    "OpenAI",
    "Linear",
    "Atlassian",
]


ACCOUNTS = [
    "saas.invoice.test1@gmail.com",
    "saas.invoice.test2@gmail.com",
    "saas.invoice.test3@gmail.com",
]


INVOICES = [
    # Account 1
    ("saas.invoice.test1@gmail.com", "Slack", "2026-09-15", "125.00", "USD","billing_portal"),
    ("saas.invoice.test1@gmail.com", "Notion", "2026-09-05", "18.00", "USD", "attachment"),
    ("saas.invoice.test1@gmail.com", "AWS", "2026-09-03", "482.71", "USD", "attachment"),
    ("saas.invoice.test1@gmail.com", "GitHub", "2026-09-08", "96.00", "USD","email_body"),
    ("saas.invoice.test1@gmail.com", "OpenAI", "2026-09-10", "220.00", "USD", "attachment"),
    ("saas.invoice.test1@gmail.com", "Linear", "2026-09-12", "80.00", "USD","attachment"),
    ("saas.invoice.test1@gmail.com", "Atlassian", "2026-09-18", "145.00", "USD","email_body"),
    ("saas.invoice.test1@gmail.com", "Google Workspace", "2026-09-20", "72.00", "USD","billing_portal"),
    ("saas.invoice.test1@gmail.com", "Notion", "2026-09-22", "25.00", "USD", "attachment"),
    ("saas.invoice.test1@gmail.com", "AWS", "2026-09-25", "315.42", "USD", "attachment"),
    ("saas.invoice.test1@gmail.com", "GitHub", "2026-09-26", "48.00", "USD", "attachment"),
    ("saas.invoice.test1@gmail.com", "Slack", "2026-09-28", "125.00", "USD", "attachment"),

    # Account 2
    ("saas.invoice.test2@gmail.com", "Notion", "2026-09-04", "22.00", "USD", "attachment"),
    ("saas.invoice.test2@gmail.com", "AWS", "2026-09-06", "731.25", "USD", "attachment"),
    ("saas.invoice.test2@gmail.com", "Google Workspace", "2026-09-07", "144.00", "USD","email_body"),
    ("saas.invoice.test2@gmail.com", "GitHub", "2026-09-09", "96.00", "USD", "attachment"),
    ("saas.invoice.test2@gmail.com", "OpenAI", "2026-09-11", "310.00", "USD","billing_portal"),
    ("saas.invoice.test2@gmail.com", "Linear", "2026-09-13", "80.00", "USD", "attachment"),
    ("saas.invoice.test2@gmail.com", "Atlassian", "2026-09-16", "210.00", "USD", "attachment"),
    ("saas.invoice.test2@gmail.com", "Slack", "2026-09-19", "250.00", "USD","email_body"),
    ("saas.invoice.test2@gmail.com", "AWS", "2026-09-21", "625.18", "USD", "attachment"),
    ("saas.invoice.test2@gmail.com", "GitHub", "2026-09-23", "144.00", "USD","billing_portal"),
    ("saas.invoice.test2@gmail.com", "OpenAI", "2026-09-24", "190.00", "USD", "attachment"),
    ("saas.invoice.test2@gmail.com", "Notion", "2026-09-27", "36.00", "USD", "attachment"),

    # Account 3
    ("saas.invoice.test3@gmail.com", "AWS", "2026-09-02", "912.33", "USD", "attachment"),
    ("saas.invoice.test3@gmail.com", "Google Workspace", "2026-09-05", "288.00", "USD","billing_portal"),
    ("saas.invoice.test3@gmail.com", "GitHub", "2026-09-08", "192.00", "USD","email_body"),
    ("saas.invoice.test3@gmail.com", "OpenAI", "2026-09-12", "450.00", "USD", "attachment"),
    ("saas.invoice.test3@gmail.com", "Linear", "2026-09-14", "120.00", "USD", "attachment"),
    ("saas.invoice.test3@gmail.com", "Atlassian", "2026-09-17", "320.00", "USD", "attachment"),
    ("saas.invoice.test3@gmail.com", "Slack", "2026-09-20", "375.00", "USD","billing_portal"),
    ("saas.invoice.test3@gmail.com", "Notion", "2026-09-22", "45.00", "USD", "attachment"),
    ("saas.invoice.test3@gmail.com", "AWS", "2026-09-24", "1184.62", "USD","email_body"),
    ("saas.invoice.test3@gmail.com", "Google Workspace", "2026-09-26", "360.00", "USD", "attachment"),
    ("saas.invoice.test3@gmail.com", "OpenAI", "2026-09-28", "275.00", "USD", "attachment"),
    ("saas.invoice.test3@gmail.com", "GitHub", "2026-09-29", "240.00", "USD", "attachment"),
]


def create_invoice_pdf(
    vendor,
    invoice_date,
    amount,
    currency,
    invoice_number,
    destination,
):
    """Create a deterministic synthetic invoice PDF."""

    pdf = canvas.Canvas(
        str(destination),
        pagesize=LETTER,
    )

    width, height = LETTER

    y = height - 80

    lines = [
        "SYNTHETIC TEST INVOICE",
        "",
        f"Vendor: {vendor}",
        f"Invoice Date: {invoice_date}",
        f"Invoice Number: {invoice_number}",
        f"Amount Due: {currency} {amount}",
        f"Currency: {currency}",
    ]

    for line in lines:
        pdf.drawString(72, y, line)
        y -= 20

    pdf.save()


def create_dataset():
    """Generate the synthetic invoice test dataset."""

    TEST_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    for index, (
        account,
        vendor,
        invoice_date,
        amount,
        currency,
        source_type,
        ) in enumerate(INVOICES, start=1):

        invoice_number = (
            f"TEST-{invoice_date.replace('-', '')}-{index:03d}"
        )

        filename = (
            f"{index:03d}_"
            f"{vendor.replace(' ', '_')}_"
            f"{invoice_date}.pdf"
        )

        destination = TEST_DATA_DIR / filename

        create_invoice_pdf(
            vendor=vendor,
            invoice_date=date.fromisoformat(invoice_date),
            amount=Decimal(amount),
            currency=currency,
            invoice_number=invoice_number,
            destination=destination,
        )

        metadata_path = destination.with_suffix(".txt")

        metadata_path.write_text(
            "\n".join(
                [
                    f"account={account}",
                    f"vendor={vendor}",
                    f"invoice_date={invoice_date}",
                    f"amount={amount}",
                    f"currency={currency}",
                    f"invoice_number={invoice_number}",
                    f"source_type={source_type}",
                ]
            ),
            encoding="utf-8",
        )

    print(
        f"Generated {len(INVOICES)} synthetic invoices "
        f"in {TEST_DATA_DIR}"
    )


if __name__ == "__main__":
    create_dataset()