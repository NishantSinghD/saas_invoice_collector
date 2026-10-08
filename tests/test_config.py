from config.loader import load_accounts, load_expected_vendors


def test_load_accounts():
    accounts = load_accounts()

    assert len(accounts) >= 1
    assert all("name" in account for account in accounts)
    assert all("email" in account for account in accounts)


def test_load_expected_vendors():
    vendors = load_expected_vendors()

    assert vendors == [
        "Slack",
        "Notion",
        "AWS",
        "Google Workspace",
        "GitHub",
        "OpenAI",
        "Linear",
        "Atlassian",
    ]