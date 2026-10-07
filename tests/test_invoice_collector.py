
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

    assert result["source_account"] == (
        "finance-test@example.com"
    )
    assert result["source_email_id"] == (
        "gmail-message-123"
    )
    assert result["file_path"].name == (
        "gmail-message-123_slack_invoice.pdf"
    )
    assert result["file_path"].read_bytes() == (
        b"fake pdf content"
    )


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
    assert captured["source_account"] == (
        "finance-test@example.com"
    )
    assert invoices == []
    assert missing == ["Notion"]


def test_processes_email_body_invoice(
    tmp_path,
    monkeypatch,
):
    message = {
        "id": "gmail-message-789",
    }

    email_body = """
    Your September 2026 invoice is ready.

    Vendor: Notion
    Invoice Date: September 20, 2026
    Invoice Number: NT-2026-09-001
    Amount: USD 20.00
    """

    monkeypatch.setattr(
        invoice_collector,
        "get_message",
        lambda service, message_id: {
            "id": message_id,
            "payload": {},
        },
    )

    monkeypatch.setattr(
        invoice_collector,
        "extract_message_body",
        lambda message: (email_body, ""),
    )

    invoices = invoice_collector.process_email_body_invoices(
        service=object(),
        messages=[message],
        output_directory=tmp_path / "invoices",
        source_account="finance-test@example.com",
    )

    assert len(invoices) == 1

    invoice = invoices[0]

    assert invoice.vendor == "Notion"
    assert invoice.invoice_date == date(2026, 9, 20)
    assert invoice.amount == 20
    assert invoice.currency == "USD"
    assert invoice.invoice_number == "NT-2026-09-001"
    assert invoice.source_type == "email_body"
    assert invoice.source_account == (
        "finance-test@example.com"
    )

    assert invoice.file_path
    assert invoice.file_path.endswith(
        "2026-09_Notion_20.00.pdf"
    )


def test_collect_and_process_invoices_includes_email_body_invoices(
    tmp_path,
    monkeypatch,
):
    message = {
        "id": "gmail-message-789",
    }

    email_body = """
    Your September 2026 invoice is ready.

    Vendor: Notion
    Invoice Date: September 20, 2026
    Invoice Number: NT-2026-09-001
    Amount: USD 20.00
    """

    monkeypatch.setattr(
        invoice_collector,
        "get_message",
        lambda service, message_id: {
            "id": message_id,
            "payload": {},
        },
    )

    monkeypatch.setattr(
        invoice_collector,
        "extract_message_body",
        lambda message: (email_body, ""),
    )

    monkeypatch.setattr(
        invoice_collector,
        "get_attachments",
        lambda message: [],
    )

    monkeypatch.setattr(
        invoice_collector,
        "detect_invoice_source",
        lambda attachments, body: "email_body",
    )

    monkeypatch.setattr(
        invoice_collector,
        "download_pdf_attachments",
        lambda service, messages, download_directory, source_account="": [],
    )

    monkeypatch.setattr(
        invoice_collector,
        "process_email_body_invoices",
        lambda service, messages, output_directory, source_account="": [
            type(
                "Invoice",
                (),
                {
                    "vendor": "Notion",
                    "invoice_date": date(2026, 9, 20),
                    "amount": 20,
                    "currency": "USD",
                    "invoice_number": "NT-2026-09-001",
                    "source_account": source_account,
                    "source_type": "email_body",
                    "file_path": str(
                        tmp_path / "2026-09_Notion_20.00.pdf"
                    ),
                },
            )()
        ],
    )

    monkeypatch.setattr(
        invoice_collector,
        "process_invoice_records",
        lambda **kwargs: ([], []),
    )

    monkeypatch.setattr(
        invoice_collector,
        "write_summary_csv",
        lambda invoices, summary_path: None,
    )

    invoices, missing = (
        invoice_collector.collect_and_process_invoices(
            service=object(),
            messages=[message],
            download_directory=tmp_path / "downloads",
            output_directory=tmp_path / "invoices",
            summary_path=tmp_path / "summary.csv",
            expected_vendors=["Notion"],
            source_account="finance-test@example.com",
        )
    )

    assert len(invoices) == 1
    assert invoices[0].vendor == "Notion"
    assert invoices[0].source_type == "email_body"
    assert missing == []


def test_attachment_source_takes_priority_over_email_body(
    tmp_path,
    monkeypatch,
):
    message = {
        "id": "gmail-message-999",
    }

    monkeypatch.setattr(
        invoice_collector,
        "get_message",
        lambda service, message_id: {
            "id": message_id,
            "payload": {},
        },
    )

    monkeypatch.setattr(
        invoice_collector,
        "extract_message_body",
        lambda message: (
            "Vendor: Slack\n"
            "Invoice Date: September 15, 2026\n"
            "Invoice Number: SL-2026-09-001\n"
            "Amount: USD 125.00",
            "",
        ),
    )

    monkeypatch.setattr(
        invoice_collector,
        "get_attachments",
        lambda message: [
            {
                "filename": "slack_invoice.pdf",
                "mime_type": "application/pdf",
                "attachment_id": "attachment-999",
            }
        ],
    )

    monkeypatch.setattr(
        invoice_collector,
        "detect_invoice_source",
        lambda attachments, body: "attachment",
    )

    pdf_invoice = type(
        "Invoice",
        (),
        {
            "vendor": "Slack",
            "invoice_date": date(2026, 9, 15),
            "amount": 125,
            "currency": "USD",
            "invoice_number": "SL-2026-09-001",
            "source_account": "finance-test@example.com",
            "source_type": "attachment",
            "file_path": str(
                tmp_path / "2026-09_Slack_125.00.pdf"
            ),
        },
    )()

    monkeypatch.setattr(
        invoice_collector,
        "download_pdf_attachments",
        lambda **kwargs: [
            {
                "file_path": tmp_path / "slack_invoice.pdf",
                "source_account": "finance-test@example.com",
                "source_email_id": "gmail-message-999",
                "email_body": "",
            }
        ],
    )

    monkeypatch.setattr(
        invoice_collector,
        "process_invoice_records",
        lambda **kwargs: ([pdf_invoice], []),
    )

    body_processor_called = False

    def fake_body_processor(**kwargs):
        nonlocal body_processor_called
        body_processor_called = True
        return []

    monkeypatch.setattr(
        invoice_collector,
        "process_email_body_invoices",
        fake_body_processor,
    )

    monkeypatch.setattr(
        invoice_collector,
        "write_summary_csv",
        lambda invoices, summary_path: None,
    )

    invoices, missing = (
        invoice_collector.collect_and_process_invoices(
            service=object(),
            messages=[message],
            download_directory=tmp_path / "downloads",
            output_directory=tmp_path / "invoices",
            summary_path=tmp_path / "summary.csv",
            expected_vendors=["Slack"],
            source_account="finance-test@example.com",
        )
    )

    assert len(invoices) == 1
    assert invoices[0].vendor == "Slack"
    assert invoices[0].source_type == "attachment"
    assert body_processor_called is False
    assert missing == []


def test_detects_billing_portal_invoice_source(
    tmp_path,
    monkeypatch,
):
    message = {
        "id": "gmail-message-portal-001",
    }

    email_body = """
    Your September 2026 invoice is ready.

    View your invoice:
    https://billing.example.com/invoices/INV-2026-09-001
    """

    monkeypatch.setattr(
        invoice_collector,
        "get_message",
        lambda service, message_id: {
            "id": message_id,
            "payload": {},
        },
    )

    monkeypatch.setattr(
        invoice_collector,
        "extract_message_body",
        lambda message: (email_body, ""),
    )

    monkeypatch.setattr(
        invoice_collector,
        "get_attachments",
        lambda message: [],
    )

    detected_source = []

    def fake_detect_source(attachments, body):
        detected_source.append(body)
        return "billing_portal"

    monkeypatch.setattr(
        invoice_collector,
        "detect_invoice_source",
        fake_detect_source,
    )

    monkeypatch.setattr(
        invoice_collector,
        "write_summary_csv",
        lambda invoices, summary_path: None,
    )

    monkeypatch.setattr(
        invoice_collector,
        "process_email_body_invoices",
        lambda **kwargs: [],
    )

    monkeypatch.setattr(
        invoice_collector,
        "process_billing_portal_invoice",
        lambda **kwargs: None,
    )

    invoices, missing = (
        invoice_collector.collect_and_process_invoices(
            service=object(),
            messages=[message],
            download_directory=tmp_path / "downloads",
            output_directory=tmp_path / "invoices",
            summary_path=tmp_path / "summary.csv",
            expected_vendors=[],
            source_account="finance-test@example.com",
        )
    )

    assert len(detected_source) == 1
    assert "billing.example.com" in detected_source[0]
    assert invoices == []
    assert missing == []


def test_collect_and_process_invoices_includes_billing_portal_invoice(
    tmp_path,
    monkeypatch,
):
    message = {
        "id": "gmail-message-portal-002",
    }

    portal_invoice = type(
        "Invoice",
        (),
        {
            "vendor": "AWS",
            "invoice_date": date(2026, 9, 25),
            "amount": 80,
            "currency": "USD",
            "invoice_number": "AWS-2026-09-001",
            "source_account": "finance-test@example.com",
            "source_type": "attachment",
            "file_path": str(
                tmp_path / "2026-09_AWS_80.00.pdf"
            ),
        },
    )()

    monkeypatch.setattr(
        invoice_collector,
        "get_message",
        lambda service, message_id: {
            "id": message_id,
            "payload": {},
        },
    )

    monkeypatch.setattr(
        invoice_collector,
        "extract_message_body",
        lambda message: (
            "Your invoice is ready: "
            "https://billing.example.com/invoices/AWS-2026-09-001",
            "",
        ),
    )

    monkeypatch.setattr(
        invoice_collector,
        "get_attachments",
        lambda message: [],
    )

    monkeypatch.setattr(
        invoice_collector,
        "detect_invoice_source",
        lambda attachments, body: "billing_portal",
    )

    monkeypatch.setattr(
        invoice_collector,
        "process_billing_portal_invoice",
        lambda **kwargs: portal_invoice,
    )

    monkeypatch.setattr(
        invoice_collector,
        "write_summary_csv",
        lambda invoices, summary_path: None,
    )

    invoices, missing = (
        invoice_collector.collect_and_process_invoices(
            service=object(),
            messages=[message],
            download_directory=tmp_path / "downloads",
            output_directory=tmp_path / "invoices",
            summary_path=tmp_path / "summary.csv",
            expected_vendors=["AWS"],
            source_account="finance-test@example.com",
        )
    )

    assert len(invoices) == 1
    assert invoices[0].vendor == "AWS"
    assert invoices[0].source_type == "attachment"
    assert missing == []