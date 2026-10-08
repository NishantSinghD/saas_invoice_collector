from pathlib import Path

from config.loader import load_accounts
from src.gmail.client import get_gmail_service
from src.gmail.invoice_collector import collect_invoices_for_date_range
from src.invoices.gaps import find_missing_vendors
from src.invoices.output import write_combined_summary_csv


def gmail_service_factory(account_name):
    """Create a Gmail API service for the specified account."""

    return get_gmail_service(account_name)


def collect_invoices_for_account(
    service,
    account_email,
    start_date,
    end_date,
    download_directory,
    output_directory,
    summary_path,
    expected_vendors,
):
    """Collect invoices for one Gmail account."""

    return collect_invoices_for_date_range(
        service=service,
        start_date=start_date,
        end_date=end_date,
        download_directory=download_directory,
        output_directory=output_directory,
        summary_path=summary_path,
        expected_vendors=expected_vendors,
        source_account=account_email,
    )


def collect_from_all_accounts(
    start_date,
    end_date,
    download_directory,
    output_directory,
    summary_directory,
    expected_vendors,
    service_factory=None,
):
    """Collect invoices from all configured Gmail accounts."""

    if service_factory is None:
        service_factory = gmail_service_factory

    all_invoices = []
    account_results = {}

    summary_directory = Path(summary_directory)
    summary_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    accounts = load_accounts()

    for account in accounts:
        account_name = account["name"]
        account_email = account["email"]

        service = service_factory(account_name)

        summary_path = (
            summary_directory
            / f"{account_name}_summary.csv"
        )

        invoices, missing_vendors = collect_invoices_for_account(
            service=service,
            account_email=account_email,
            start_date=start_date,
            end_date=end_date,
            download_directory=download_directory,
            output_directory=output_directory,
            summary_path=summary_path,
            expected_vendors=expected_vendors,
        )

        all_invoices.extend(invoices)

        account_results[account_email] = {
            "invoices": invoices,
            "missing_vendors": missing_vendors,
        }

    combined_missing_vendors = find_missing_vendors(
        expected_vendors,
        all_invoices,
    )

    combined_summary_path = (
        summary_directory / "combined_summary.csv"
    )

    write_combined_summary_csv(
        all_invoices,
        combined_summary_path,
    )

    return all_invoices, {
        "accounts": account_results,
        "missing_vendors": combined_missing_vendors,
    }