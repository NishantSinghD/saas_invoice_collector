# SaaS Invoice Collection

## 1. Goal

Automate the collection of SaaS invoices from 3 Gmail accounts for a given month and organise them into a single location.

## 2. Input

- 3 Gmail accounts
- Target month
- Expected vendor list

## 3. Workflow

3 Gmail accounts
→ Find invoice emails for the target month
→ Identify invoice emails
→ Locate the invoice:
  - PDF attachment
  - Billing portal link
  - Invoice in email body
→ Obtain invoice as PDF
→ Extract invoice information
→ Validate and deduplicate
→ Save invoice PDF
→ Generate summary
→ Check expected vendors
→ Flag potential gaps

## 4. Output

- Invoice PDFs
- Summary CSV
- Potential invoice gaps

## 5. Invoice Data Model

Each collected invoice will contain:

- Vendor
- Invoice date
- Amount
- Currency
- Invoice number
- Source Gmail account
- Source email ID
- Invoice source type: attachment, billing_portal, email_body
- Local file path
- Processing status

## 6. Test Cases

### Normal cases

1. Invoice with PDF attachment
2. Invoice in email body
3. Invoice with billing portal link
4. Invoice with multiple attachments
5. Invoice in USD
6. Invoice in INR

### Edge cases

7. Duplicate invoice
8. Non-invoice email from a SaaS vendor
9. Invoice with unusual PDF filename
10. Invoice with missing metadata
11. Invoice from an unexpected vendor
12. Invoice forwarded from another email address
13. Invoice with multiple URLs
14. Email outside the target month
15. Invoice with an amount containing commas

## 7. Expected Vendors

- Slack
- Notion
- AWS
- Google Workspace
- GitHub
- OpenAI
- Linear
- Atlassian