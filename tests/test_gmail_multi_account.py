from src.gmail import multi_account


def test_gmail_service_factory_uses_account_name(
    monkeypatch,
):
    captured = {}

    def fake_get_gmail_service(account_name):
        captured["account_name"] = account_name
        return "fake-gmail-service"

    monkeypatch.setattr(
        multi_account,
        "get_gmail_service",
        fake_get_gmail_service,
    )

    service = multi_account.gmail_service_factory(
        "finance_account_2"
    )

    assert service == "fake-gmail-service"
    assert captured["account_name"] == (
        "finance_account_2"
    )