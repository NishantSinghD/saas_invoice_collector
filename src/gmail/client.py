from src.gmail.parser import (
    extract_message_body,
    get_attachments,
    get_headers,
)
from googleapiclient.discovery import build

from src.gmail.auth import get_credentials


def get_gmail_service():
    """Return an authenticated Gmail API service."""

    credentials = get_credentials()

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
    """Retrieve Gmail messages received within a date range."""

    query = f"after:{start_date} before:{end_date}"

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


if __name__ == "__main__":
    service = get_gmail_service()

    messages = get_recent_messages(service)

    print(f"Found {len(messages)} messages.")

    if messages:
        message = get_message(
            service,
            messages[0]["id"],
        )

        headers = get_headers(message)
        plain_text, html = extract_message_body(message)
        attachments = get_attachments(message)
        print(f"From: {headers.get('from', '(unknown)')}")
        print(f"Subject: {headers.get('subject', '(unknown)')}")
        print(f"Date: {headers.get('date', '(unknown)')}")

        print("\nPlain-text body:")
        print(plain_text[:500])

        print("\nHTML body:")
        print(html[:500])
        print("\nAttachments:")

for attachment in attachments:
    print(
        f"- {attachment['filename']} "
        f"({attachment['mime_type']})"
    )