from datetime import date
from src.invoices.models import InvoiceData
from src.gmail import multi_account


def test_collect_invoices_for_account(
    tmp_path,
    monkeypatch,
):
    captured = {}

    expected_invoices = [
        "invoice-1",
    ]

    expected_missing = [
        "Notion",
    ]

    def fake_collect(
        service,
        start_date,
        end_date,
        download_directory,
        output_directory,
        summary_path,
        expected_vendors,
        source_account,
    ):
        captured["service"] = service
        captured["start_date"] = start_date
        captured["end_date"] = end_date
        captured["source_account"] = source_account
        captured["summary_path"] = summary_path

        return expected_invoices, expected_missing

    monkeypatch.setattr(
        multi_account,
        "collect_invoices_for_date_range",
        fake_collect,
    )

    invoices, missing = (
        multi_account.collect_invoices_for_account(
            service="fake-service",
            account_email="finance1@example.com",
            start_date=date(2026, 9, 1),
            end_date=date(2026, 10, 1),
            download_directory=tmp_path / "downloads",
            output_directory=tmp_path / "invoices",
            summary_path=tmp_path / "summary.csv",
            expected_vendors=["Slack", "Notion"],
        )
    )

    assert invoices == expected_invoices
    assert missing == expected_missing

    assert captured["service"] == "fake-service"
    assert captured["start_date"] == date(2026, 9, 1)
    assert captured["end_date"] == date(2026, 10, 1)
    assert captured["source_account"] == "finance1@example.com"
    assert captured["summary_path"] == tmp_path / "summary.csv"

def test_collect_from_all_accounts(
    tmp_path,
    monkeypatch,
):
    accounts = [
        {
            "name": "finance_account_1",
            "email": "finance1@example.com",
        },
        {
            "name": "finance_account_2",
            "email": "finance2@example.com",
        },
        {
            "name": "finance_account_3",
            "email": "finance3@example.com",
        },
    ]

    monkeypatch.setattr(
        multi_account,
        "load_accounts",
        lambda: accounts,
    )

    service_calls = []
    account_calls = []

    def fake_service_factory(account_name):
        service_calls.append(account_name)
        return f"service-{account_name}"

    def fake_collect(
        service,
        account_email,
        start_date,
        end_date,
        download_directory,
        output_directory,
        summary_path,
        expected_vendors,
    ):
        account_calls.append(
            {
                "service": service,
                "account_email": account_email,
                "summary_path": summary_path,
            }
        )

        return (
            [
                InvoiceData(
                    vendor="Slack",
                    invoice_date=date(2026, 9, 15),
                    amount=125,
                    currency="USD",
                    invoice_number=f"INV-{account_email}",
                    source_account=account_email,
                    source_type="attachment",
                    file_path=str(
                        tmp_path
                        / f"{account_email}_invoice.pdf"
                    ),
                )
            ],
            [f"missing-{account_email}"],
        )

    monkeypatch.setattr(
        multi_account,
        "collect_invoices_for_account",
        fake_collect,
    )

    invoices, results = (
        multi_account.collect_from_all_accounts(
            service_factory=fake_service_factory,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 10, 1),
            download_directory=tmp_path / "downloads",
            output_directory=tmp_path / "invoices",
            summary_directory=tmp_path / "summaries",
            expected_vendors=["Slack", "Notion"],
        )
    )

    assert service_calls == [
        "finance_account_1",
        "finance_account_2",
        "finance_account_3",
    ]

    assert len(account_calls) == 3

    assert account_calls[0]["account_email"] == (
        "finance1@example.com"
    )
    assert account_calls[1]["account_email"] == (
        "finance2@example.com"
    )
    assert account_calls[2]["account_email"] == (
        "finance3@example.com"
    )

    assert len(invoices) == 3

    assert [
        invoice.source_account
        for invoice in invoices
    ] == [
        "finance1@example.com",
        "finance2@example.com",
        "finance3@example.com",
    ]
    assert results["accounts"]["finance1@example.com"]["missing_vendors"] == [
    "missing-finance1@example.com",
    ]

    assert results["accounts"]["finance2@example.com"]["missing_vendors"] == [
        "missing-finance2@example.com",
    ]

    assert results["accounts"]["finance3@example.com"]["missing_vendors"] == [
        "missing-finance3@example.com",
    ]

    assert results["missing_vendors"] == [
        "Notion",
    ]