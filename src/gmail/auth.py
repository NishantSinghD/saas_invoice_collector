from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly"
]

BASE_DIR = Path(__file__).resolve().parents[2]
CREDENTIALS_DIR = BASE_DIR / "credentials"

CLIENT_SECRET_FILE = next(
    CREDENTIALS_DIR.glob("client_secret_*.json")
)


def get_token_file(account_name):
    """Return the token file path for a Gmail account."""

    safe_account_name = (
        account_name
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("@", "_at_")
        .replace(".", "_")
    )

    return CREDENTIALS_DIR / (
        f"token_{safe_account_name}.json"
    )


def get_credentials(account_name):
    """Authenticate a Gmail account and return its credentials."""

    token_file = get_token_file(account_name)

    credentials = None

    if token_file.exists():
        credentials = Credentials.from_authorized_user_file(
            token_file,
            SCOPES,
        )

    if credentials is None or not credentials.valid:

        if (
            credentials
            and credentials.expired
            and credentials.refresh_token
        ):
            credentials.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE,
                SCOPES,
            )

            credentials = flow.run_local_server(
                port=0
            )

        token_file.write_text(
            credentials.to_json()
        )

    return credentials