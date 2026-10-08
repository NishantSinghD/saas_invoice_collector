from pathlib import Path

import yaml


BASE_DIR = Path(__file__).resolve().parents[1]
ACCOUNTS_FILE = BASE_DIR / "config" / "accounts.yaml"
VENDORS_FILE = BASE_DIR / "config" / "vendors.yaml"


def load_accounts():
    """Load Gmail account configuration from YAML."""
    with ACCOUNTS_FILE.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    accounts = config.get("accounts", [])

    if not accounts:
        raise ValueError("No Gmail accounts configured.")

    return accounts


def load_expected_vendors():
    """Load the expected SaaS vendor list from YAML."""
    with VENDORS_FILE.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    vendors = config.get("expected_vendors", [])

    if not vendors:
        raise ValueError("No expected vendors configured.")

    return vendors


def load_vendor_aliases():
    """Load vendor name aliases from YAML."""
    with VENDORS_FILE.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    return config.get("vendor_aliases", {})