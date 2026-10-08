# SaaS Invoice Collector

Automated pipeline for collecting monthly SaaS invoices from multiple Gmail accounts, extracting invoice data, deduplicating records, saving standardized PDF files, generating CSV summaries, and flagging missing expected vendors.

## 1. What it does

The system is designed to collect invoices for a specified month from multiple Gmail accounts.

It supports three invoice sources:

1. **PDF attachment** - invoice is attached directly to the email.
2. **Billing portal link** - email contains a direct URL that returns a PDF invoice.
3. **Email body** - invoice information is contained directly in the email body.

For each invoice, the pipeline:

- Identifies the invoice source.
- Extracts vendor, invoice date, amount, currency, and invoice number.
- Uses deterministic extraction first.
- Falls back to a local Ollama/Qwen model when the invoice format is ambiguous.
- Deduplicates invoices using file hashes and invoice identity.
- Saves invoices using the format:

```text
YYYY-MM_Vendor_Amount.pdf
```

- Generates per-account and combined CSV summaries.
- Detects expected vendors that were not found.

### Expected vendors

The default configuration expects:

- Slack
- Notion
- AWS
- Google Workspace
- GitHub
- OpenAI
- Linear
- Atlassian

Vendor aliases can be configured in `config/vendors.yaml`.

---

## 2. Architecture

```text
                    ┌──────────────────────┐
                    │   Gmail Accounts     │
                    │      1 / 2 / 3       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Gmail Collector   │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┼─────────────┐
                 ▼             ▼             ▼
            PDF Attachment  Portal URL   Email Body
                 │             │             │
                 └─────────────┼─────────────┘
                               ▼
                    ┌──────────────────────┐
                    │   Invoice Processor  │
                    │                      │
                    │ Deterministic → LLM  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   InvoiceData Model  │
                    └──────────┬───────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
              Deduplication          Vendor Gaps
                    │                     │
                    ▼                     ▼
             Invoice PDFs          Missing Vendors
                    │
                    ▼
              Summary CSVs
```

---

## 3. Project structure

```text
saas-invoice-collector/
│
├── config/
│   ├── accounts.yaml       # Gmail accounts
│   ├── vendors.yaml        # Expected vendors and aliases
│   └── loader.py           # Configuration loading
│
├── src/
│   ├── gmail/
│   │   ├── auth.py         # Gmail OAuth authentication
│   │   ├── client.py       # Gmail API operations
│   │   ├── parser.py       # Email/body/attachment parsing
│   │   ├── invoice_collector.py
│   │   └── multi_account.py
│   │
│   ├── invoices/
│   │   ├── detector.py
│   │   ├── source_detector.py
│   │   ├── portal.py
│   │   ├── models.py
│   │   ├── extractor.py
│   │   ├── llm_extractor.py
│   │   ├── pdf_reader.py
│   │   ├── processor.py
│   │   ├── deduplication.py
│   │   ├── output.py
│   │   └── gaps.py
│   │
│   └── pipeline.py
│
├── tests/
├── sample_data/
├── output/
├── credentials/
├── run.py
├── requirements.txt
├── pytest.ini
└── .gitignore
```

---

## 4. Prerequisites

- Python 3.11+
- Gmail API access
- Google OAuth client credentials
- Ollama
- Qwen 2.5 3B (used as the local extraction fallback)

The LLM component runs locally through Ollama. No external LLM API key is required.

---

## 5. Installation

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

---

## 6. Gmail OAuth setup

Create a Gmail API OAuth desktop application in Google Cloud.

Place the downloaded OAuth client JSON file inside:

```text
credentials/
```

The application automatically creates a separate token file for each configured account.

For example:

```text
credentials/
├── client_secret_....json
├── token_finance_account_1.json
├── token_finance_account_2.json
└── token_finance_account_3.json
```

OAuth tokens are deliberately excluded from Git through `.gitignore`.

### Configure accounts

Edit:

```text
config/accounts.yaml
```

Example:

```yaml
accounts:
  - name: finance_account_1
    email: account1@example.com

  - name: finance_account_2
    email: account2@example.com

  - name: finance_account_3
    email: account3@example.com
```

Each account is authenticated independently.

---

## 7. Ollama setup

Install Ollama and pull the extraction model:

```powershell
ollama pull qwen2.5:3b
```

Ollama should be running locally at:

```text
http://127.0.0.1:11434
```

The application communicates with Ollama through its local HTTP API.

No Ollama account or external API subscription is required.

---

## 8. Configure expected vendors

Edit:

```text
config/vendors.yaml
```

Example:

```yaml
expected_vendors:
  - Slack
  - Notion
  - AWS
  - Google Workspace
  - GitHub
  - OpenAI
  - Linear
  - Atlassian

vendor_aliases:
  Slack:
    - Slack
    - Slack Technologies
  AWS:
    - AWS
    - Amazon Web Services
  Google Workspace:
    - Google Workspace
    - Google
  GitHub:
    - GitHub
    - GitHub Inc.
  OpenAI:
    - OpenAI
    - OpenAI Inc.
  Atlassian:
    - Atlassian
    - Atlassian Corporation
```

Aliases prevent legitimate vendor-name variations from being incorrectly reported as missing.

---

## 9. Run the collector

Specify the invoice month using `YYYY-MM`.

For September 2026:

```powershell
python run.py --month 2026-09
```

The pipeline processes all configured Gmail accounts and produces:

```text
output/
├── combined_summary.csv
├── finance_account_1_summary.csv
├── finance_account_2_summary.csv
├── finance_account_3_summary.csv
├── missing_vendors.csv
└── invoices/
    └── YYYY-MM_Vendor_Amount.pdf
```

---

## 10. Output format

### Invoice filename

Invoices are saved as:

```text
YYYY-MM_Vendor_Amount.pdf
```

Example:

```text
2026-09_Slack_125.00.pdf
```

### Summary CSV

The combined summary contains:

```text
vendor
date
amount
currency
source_account
source_type
file_link
```

Example:

```text
Slack,2026-09-15,125.00,USD,account@example.com,attachment,...
```

### Missing vendors

`missing_vendors.csv` contains expected vendors that were not found for the requested month.

---

## 11. Extraction strategy

The extraction process intentionally uses a two-stage approach.

### Stage 1 — deterministic extraction

Known invoice formats are processed using regular expressions and explicit parsing rules.

This is:

- Fast
- Predictable
- Cheap
- Easy to test

### Stage 2 — local LLM fallback

If deterministic extraction cannot identify all required fields, the invoice text is sent to the local Qwen model through Ollama.

The model is constrained to return a structured schema containing:

```text
vendor
invoice_date
amount
currency
invoice_number
```

The result is validated using Pydantic before being converted into the application's `InvoiceData` model.

This allows the pipeline to handle invoices whose layouts differ from the expected deterministic format.

---

## 12. Deduplication

Invoices are deduplicated using two mechanisms:

### File hash

A SHA-256 hash identifies identical files.

### Invoice identity

Invoices are also compared using:

```text
vendor
invoice_number
invoice_date
amount
currency
```

This protects against duplicate emails containing the same invoice.

---

## 13. What is automated vs. manual

### Automated

- Gmail account iteration
- Gmail message retrieval
- Email parsing
- PDF attachment detection
- Invoice source detection
- PDF text extraction
- Deterministic invoice extraction
- Local LLM fallback
- Structured data validation
- Invoice date filtering
- Duplicate detection
- Invoice PDF naming and saving
- Per-account summaries
- Combined summary
- Missing-vendor detection

### Manual / one-time setup

- Creating the Google Cloud OAuth application
- Placing the OAuth client credentials in `credentials/`
- Authenticating each Gmail account the first time
- Installing Ollama
- Downloading the Qwen model
- Configuring Gmail accounts and expected vendors

After setup, the normal monthly workflow is:

```powershell
python run.py --month YYYY-MM
```

---

## 14. Testing

Run the complete automated test suite with:

```powershell
pytest -q
```

The current implementation has:

```text
50 passed
```

The test suite covers configuration loading, extraction, invoice processing, output generation, source handling, deduplication, and multi-account collection.

Synthetic invoice data is used for repeatable testing without exposing production invoice data.

---

## 15. Current limitations

### Billing portals

The current implementation supports billing links that directly return a PDF.

It does **not** implement generic browser automation or authenticated login flows for arbitrary SaaS billing portals.

### OCR

PDF text extraction currently relies on text embedded in the PDF.

Scanned/image-only invoices requiring OCR are not currently supported.

### Google Sheets

The current output is CSV rather than a live Google Sheet.

The CSV structure is designed so that a Google Sheets integration can be added as a downstream output step.

### Gmail search

Gmail retrieval currently starts from messages after the beginning of the requested month. The final invoice date is validated from the extracted invoice itself.

This avoids relying solely on Gmail message timestamps because an email's received date and an invoice's actual billing date can differ.

### Filename collisions

The requested filename format does not include the invoice number. Therefore, two different invoices from the same vendor with the same month and amount could require additional collision handling in a future version.

---

## 16. Design decisions

### Why deterministic extraction before an LLM?

Most SaaS invoices have relatively predictable fields. Deterministic extraction is therefore preferable when possible because it is faster, cheaper, and easier to validate.

The LLM is used as a fallback rather than as the primary parser.

### Why a local LLM?

The assignment requires handling potentially sensitive financial documents.

Using Ollama locally means invoice contents do not need to be sent to an external LLM API.

### Why process multiple Gmail accounts independently?

Each account has its own OAuth token and Gmail service. Processing accounts independently provides:

- Account-level auditability
- Separate summaries
- Easier failure isolation
- Clear source-account attribution

The results are then combined into a single summary.

---

## 17. Example

Running:

```powershell
python run.py --month 2026-09
```

can produce an output such as:

```text
Processed invoices: 1

Slack | 2026-09-15 | 125.00 USD | account@example.com

Missing expected vendors:
- Notion
- AWS
- Google Workspace
- GitHub
- OpenAI
- Linear
- Atlassian
```

The missing-vendor list is intentional: it distinguishes between "no invoice found" and "invoice successfully collected."

---

## 18. Future extensions

The architecture can be extended with:

1. Google Sheets output
2. OCR for scanned invoices
3. Browser automation for authenticated billing portals
4. Vendor-specific extraction adapters
5. Retry/error queues
6. Persistent processing state
7. Cloud deployment
8. Scheduled monthly execution
9. Notifications when invoices are missing
10. Stronger invoice filename collision handling