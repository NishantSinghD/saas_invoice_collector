from googleapiclient.discovery import build

from src.gmail.auth import get_credentials
from src.gmail.parser import get_attachments


def get_gmail_service(account_name):
    """Authenticate and return a Gmail API service for an account."""

    from googleapiclient.discovery import build

    credentials = get_credentials(account_name)

    return build(
        "gmail",
        "v1",
        credentials=credentials,
    )


def get_recent_messages(service, max_results=10):
    """Retrieve recent Gmail messages."""

    response = (
        service.users()
        .messages()
        .list(
            userId="me",
            maxResults=max_results,
        )
        .execute()
    )

    return response.get("messages", [])


def get_messages_for_date_range(service, start_date, end_date):
    """Retrieve candidate Gmail messages from the start date onward."""

    start = start_date.strftime("%Y/%m/%d")
    query = f"after:{start}"

    print(f"Gmail query: {query}")

    response = (
        service.users()
        .messages()
        .list(
            userId="me",
            q=query,
        )
        .execute()
    )

    return response.get("messages", [])

def get_message_subject(service, message_id):
    """Retrieve the subject of a Gmail message."""

    message = (
        service.users()
        .messages()
        .get(
            userId="me",
            id=message_id,
            format="metadata",
            metadataHeaders=["Subject"],
        )
        .execute()
    )

    headers = message.get("payload", {}).get("headers", [])

    return next(
        (
            header["value"]
            for header in headers
            if header["name"].lower() == "subject"
        ),
        "(No subject)",
    )


def get_message(service, message_id):
    """Retrieve a complete Gmail message."""

    return (
        service.users()
        .messages()
        .get(
            userId="me",
            id=message_id,
            format="full",
        )
        .execute()
    )


def download_attachment(service, message_id, attachment_id):
    """Download a Gmail attachment and return its raw bytes."""

    import base64

    response = (
        service.users()
        .messages()
        .attachments()
        .get(
            userId="me",
            messageId=message_id,
            id=attachment_id,
        )
        .execute()
    )

    return base64.urlsafe_b64decode(
        response["data"]
    )


if __name__ == "__main__":
    service = get_gmail_service()

    messages = get_recent_messages(service)

    print(f"Found {len(messages)} messages.")

    for message in messages:
        subject = get_message_subject(
            service,
            message["id"],
        )

        print(f"- {subject}")