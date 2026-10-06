import base64


def decode_body(data):
    """Decode a Gmail API base64url-encoded body."""

    if not data:
        return ""

    return base64.urlsafe_b64decode(data).decode(
        "utf-8",
        errors="replace",
    )


def get_headers(message):
    """Return Gmail message headers as a dictionary."""

    headers = message.get("payload", {}).get("headers", [])

    return {
        header["name"].lower(): header["value"]
        for header in headers
    }


def extract_message_body(message):
    """Extract plain-text and HTML content from a Gmail message."""

    plain_text = ""
    html = ""

    def walk_parts(part):
        nonlocal plain_text, html

        mime_type = part.get("mimeType", "")
        body_data = part.get("body", {}).get("data")

        if body_data:
            decoded = decode_body(body_data)

            if mime_type == "text/plain":
                plain_text += decoded

            elif mime_type == "text/html":
                html += decoded

        for child in part.get("parts", []):
            walk_parts(child)

    payload = message.get("payload", {})
    walk_parts(payload)

    return plain_text, html


def get_attachments(message):
    """Return metadata for attachments in a Gmail message."""

    attachments = []

    def walk_parts(part):
        filename = part.get("filename")
        body = part.get("body", {})
        attachment_id = body.get("attachmentId")

        if filename and attachment_id:
            attachments.append(
                {
                    "filename": filename,
                    "mime_type": part.get("mimeType", ""),
                    "attachment_id": attachment_id,
                }
            )

        for child in part.get("parts", []):
            walk_parts(child)

    payload = message.get("payload", {})
    walk_parts(payload)

    return attachments