# Tax Invoice Webhook Guide

## Overview

The tax invoice webhook automatically generates and sends tax invoices for leads in the "Generate tax invoice" status in Kommo.

## Endpoint

**URL:** `POST /webhook/generate-tax-invoice?token=YOUR_TOKEN`

**Authentication:** Webhook token (query parameter)

## How It Works

1. **Webhook is triggered** by Kommo (or manually)
2. **Validates token** from query parameter
3. **Returns immediately** (202 Accepted)
4. **Background processing:**
   - Fetches leads from "Generate tax invoice" status
   - Filters out leads with "tax_invoice" tag (already processed)
   - Processes up to 3 leads per webhook call
   - For each lead:
     - Fetches contact and product details
     - Generates tax invoice JSON
     - Creates PDF invoice
     - Sends email to customer
     - Adds "tax_invoice" tag to lead

## Differences from Proforma Invoice

### Payment Terms
- **Tax Invoice:** Always "Payment on Delivery" (hardcoded)
- **Proforma Invoice:** Uses "Payment Terms" field from Kommo, includes deposit amount

### Invoice Number Format
- **Tax Invoice:** `TAXZS-00001` (TAXZS-{lead_id})
- **Proforma Invoice:** `00PI25-00000001` (00PI25-{lead_id})

### Tag Added
- **Tax Invoice:** `tax_invoice`
- **Proforma Invoice:** `proforma`

### Status ID
- **Tax Invoice:** Status ID in `GENERATE_TAX_INVOICE_STATUS_ID` constant
- **Proforma Invoice:** Status ID in `GENERATE_PROFORMA_STATUS_ID` constant

## Configuration

### 1. Update Status ID

In `kommo_helper.py`, update the status ID for your tax invoice status:

```python
GENERATE_TAX_INVOICE_STATUS_ID = 94720977  # Update with your actual status ID
```

To find your status ID:
1. Go to Kommo pipeline settings
2. Find the "Generate tax invoice" status
3. Get the status ID from the URL or API

### 2. Set Webhook Token

In your `.env` file:

```env
WEBHOOK_TOKEN=your-secret-webhook-token-here
```

### 3. Configure Kommo Webhook

In Kommo settings, add webhook:
- **URL:** `https://your-domain.com/webhook/generate-tax-invoice?token=your-secret-webhook-token-here`
- **Trigger:** When lead moves to "Generate tax invoice" status
- **Method:** POST

## Testing

### Manual Test

```bash
curl -X POST "http://localhost:8000/webhook/generate-tax-invoice?token=your-token"
```

### Check Logs

The webhook logs all processing steps:
- Leads fetched
- Leads filtered (already processed)
- Invoice generation
- Email sending
- Tag adding

## Email Content

Subject: `Tax Invoice {invoice_number} - {customer_name}`

The email includes:
- Invoice number
- Date of issuing
- Total amount (AED)
- PDF attachment: `TaxInvoice_{invoice_number}.pdf`

## Invoice Details

The tax invoice includes:
- **Title:** "TAX INVOICE" (not "PROFORMA INVOICE")
- **Payment Terms:** "Payment on Delivery" (hardcoded)
- **All product details** from catalog
- **Discount** from lead's "Discount" field
- **Customer details** from contact
- **Company stamp and signature**

## Lead Requirements

Each lead must have:
1. ✅ At least one contact with email
2. ✅ At least one product in catalog
3. ✅ Delivery address (optional but recommended)
4. ✅ Customer TRN (optional but recommended)

## Processing Limits

- **Per webhook call:** Maximum 3 leads
- **Already processed leads:** Skipped (have "tax_invoice" tag)
- **Missing data leads:** Skipped with warning in logs

## Status Codes

- `202 Accepted` - Webhook received, processing in background
- `401 Unauthorized` - Invalid webhook token
- `500 Internal Server Error` - Server error

## Troubleshooting

### No invoices generated
- Check logs for lead processing details
- Verify leads are in correct status
- Check leads don't already have "tax_invoice" tag
- Verify leads have required contact and product data

### Email not sent
- Check `RESEND_API_KEY` is configured
- Check `FROM_EMAIL` is configured
- Verify contact has valid email address
- Check Resend dashboard for delivery status

### Wrong status leads
- Verify `GENERATE_TAX_INVOICE_STATUS_ID` matches your Kommo status
- Check pipeline ID is correct

## Related Files

- `kommo_helper.py` - Helper functions for fetching and preparing data
- `generate_tax_invoice.py` - HTML template for tax invoices
- `main.py` - Webhook endpoint and background processing
- `convert_to_pdf.py` - PDF generation from HTML

