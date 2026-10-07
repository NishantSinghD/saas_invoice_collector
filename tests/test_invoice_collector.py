
from datetime import date
from src.gmail import invoice_collector


def test_downloads_pdf_attachment_and_preserves_email_metadata(
    tmp_path,
    monkeypatch,
):
    message = {"id": "gmail-message-123"}

    monkeypatch.setattr(
        invoice_collector,
        "get_message",
        lambda service, message_id: {"id": message_id},
    )

    monkeypatch.setattr(
        invoice_collector,
        "get_attachments",
        lambda message: [
            {
                "filename": "slack_invoice.pdf",
                "mime_type": "application/pdf",
                "attachment_id": "attachment-123",
            },
            {
                "filename": "notes.txt",
                "mime_type": "text/plain",
                "attachment_id": "attachment-456",
            },
        ],
    )

    monkeypatch.setattr(
        invoice_collector,
        "download_attachment",
        lambda service, message_id, attachment_id: (
            b"fake pdf content"
        ),
    )

    results = invoice_collector.download_pdf_attachments(
        service=object(),
        messages=[message],
        download_directory=tmp_path,
        source_account="finance-test@example.com",
    )

    assert len(results) == 1

    result = results[0]

    assert result["source_account"] == "finance-test@example.com"
    assert result["source_email_id"] == "gmail-message-123"
    assert result["file_path"].name == (
        "gmail-message-123_slack_invoice.pdf"
    )
    assert result["file_path"].read_bytes() == b"fake pdf content"


def test_returns_empty_list_when_no_pdf_attachments(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        invoice_collector,
        "get_message",
        lambda service, message_id: {"id": message_id},
    )

    monkeypatch.setattr(
        invoice_collector,
        "get_attachments",
        lambda message: [
            {
                "filename": "notes.txt",
                "mime_type": "text/plain",
                "attachment_id": "attachment-456",
            },
        ],
    )

    results = invoice_collector.download_pdf_attachments(
        service=object(),
        messages=[{"id": "gmail-message-456"}],
        download_directory=tmp_path,
    )

    assert results == []

def test_collect_invoices_for_date_range_uses_requested_dates(
    tmp_path,
    monkeypatch,
):
    from src.gmail import invoice_collector

    captured = {}

    def fake_search(service, start_date, end_date):
        captured["start_date"] = start_date
        captured["end_date"] = end_date
        return [{"id": "message-123"}]

    def fake_process(**kwargs):
        captured["messages"] = kwargs["messages"]
        captured["source_account"] = kwargs["source_account"]
        return [], ["Notion"]

    monkeypatch.setattr(
        invoice_collector,
        "get_messages_for_date_range",
        fake_search,
    )

    monkeypatch.setattr(
        invoice_collector,
        "collect_and_process_invoices",
        fake_process,
    )

    invoices, missing = (
        invoice_collector.collect_invoices_for_date_range(
            service=object(),
            start_date="2026/09/01",
            end_date="2026/10/01",
            download_directory=tmp_path / "downloads",
            output_directory=tmp_path / "invoices",
            summary_path=tmp_path / "summary.csv",
            expected_vendors=["Slack", "Notion"],
            source_account="finance-test@example.com",
        )
    )

    assert captured["start_date"] == "2026/09/01"
    assert captured["end_date"] == "2026/10/01"
    assert captured["messages"] == [{"id": "message-123"}]
    assert captured["source_account"] == "finance-test@example.com"
    assert invoices == []
    assert missing == ["Notion"]
