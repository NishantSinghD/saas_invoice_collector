import argparse
from calendar import monthrange
from datetime import date
from pathlib import Path
from src.invoices.output import write_missing_vendors_csv
from config.loader import load_expected_vendors
from src.gmail.multi_account import collect_from_all_accounts


BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_DIRECTORY = BASE_DIR / "output" / "downloads"
OUTPUT_DIRECTORY = BASE_DIR / "output" / "invoices"
SUMMARY_DIRECTORY = BASE_DIR / "output"


def parse_month(month_text):
    """Convert YYYY-MM into the first and last day of that month."""

    try:
        year, month = map(int, month_text.split("-"))
        start_date = date(year, month, 1)
    except ValueError:
        raise ValueError(
            "Month must be in YYYY-MM format, for example 2026-09."
        )

    last_day = monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    return start_date, end_date


def main():
    parser = argparse.ArgumentParser(
        description="Collect SaaS invoices from multiple Gmail accounts."
    )

    parser.add_argument(
        "--month",
        required=True,
        help="Invoice month in YYYY-MM format, for example 2026-09.",
    )

    args = parser.parse_args()

    start_date, end_date = parse_month(args.month)

    expected_vendors = load_expected_vendors()

    print(f"Collecting invoices for {start_date:%Y-%m-%d}")
    print(f"Invoice date range: {start_date} to {end_date}")
    print()

    invoices, results = collect_from_all_accounts(
    start_date=start_date,
    end_date=end_date,
    expected_vendors=expected_vendors,
    download_directory=DOWNLOAD_DIRECTORY,
    output_directory=OUTPUT_DIRECTORY,
    summary_directory=SUMMARY_DIRECTORY,
    )

    print()
    print(f"Processed invoices: {len(invoices)}")
    print()

    for invoice in invoices:
        print(
            f"{invoice.vendor} | "
            f"{invoice.invoice_date} | "
            f"{invoice.amount} {invoice.currency} | "
            f"{invoice.source_account}"
        )

    print()

    missing_vendors = results["missing_vendors"]
    missing_vendors_path = (
        SUMMARY_DIRECTORY / "missing_vendors.csv"
    )

    write_missing_vendors_csv(
        missing_vendors,
        missing_vendors_path,
    )
    if missing_vendors:
        print("Missing expected vendors:")
        for vendor in missing_vendors:
            print(f"- {vendor}")
    else:
        print("All expected vendors were found.")


if __name__ == "__main__":
    main()