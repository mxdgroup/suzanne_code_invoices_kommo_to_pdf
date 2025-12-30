# Webhook Integration Guide

## Overview

The invoice API now includes a webhook endpoint that automatically generates proforma invoices for leads in the "Generate pro forma" status from Kommo CRM.

## Endpoint

```
POST /webhook/generate-proforma?token={WEBHOOK_TOKEN}
```

## How It Works

1. **Trigger**: Webhook is called (manually or via Kommo automation)
2. **Fetch**: Gets all leads from "Generate pro forma" status (ID: 94720975)
3. **Filter**: Processes only leads WITHOUT the "proforma" tag
4. **Limit**: Processes up to 3 leads per webhook call
5. **Generate**: Creates proforma invoice PDF and emails it to the customer
6. **Tag**: Adds "proforma" tag to successfully processed leads
7. **Database**: Stores invoice data in MongoDB for future tax invoice generation

## Configuration

### Environment Variables

Add these to your `.env` file:

```env
# Webhook token for validation
WEBHOOK_TOKEN=your-secure-webhook-token-here

# Kommo CRM credentials
KOMMO_SUBDOMAIN=your-subdomain
KOMMO_ACCESS_TOKEN=your-kommo-access-token

# Existing variables
API_SECRET_TOKEN=your-api-secret-token
RESEND_API_KEY=your-resend-api-key
FROM_EMAIL=invoices@suzannecode.com
MONGODB_URI=your-mongodb-connection-string
```

### Kommo Lead Requirements

For a lead to be processed successfully, it must have:

1. **Contact** with:
   - Name
   - Email address (used for sending invoice)
   - TRN (optional)

2. **Lead Custom Fields**:
   - Delivery address
   - Payment Terms (defaults to "Advance payment of 50% before Delivery")
   - Discount (optional, e.g., "5%", "10%", "No discount")
   - Payment type (e.g., "Deposit")
   - Deposit Amount (if payment type includes "deposit")

3. **Products** (catalog elements) with:
   - Product name
   - SKU (optional)
   - Product Details (optional)
   - Price (AED) - must include VAT
   - Unit (defaults to "Pcs")
   - Quantity

## Testing the Webhook

### Manual Testing

```bash
curl -X POST "https://your-domain.com/webhook/generate-proforma?token=your-webhook-token"
```

### Expected Response

```json
{
  "status": "success",
  "message": "Processed 2/2 leads",
  "leads_found": 2,
  "leads_processed": 2,
  "results": [
    {
      "lead_id": 21504847,
      "lead_name": "Test lead - Don't delete",
      "status": "success",
      "invoice_number": "00PI25-21504847",
      "emails_sent_to": ["customer@example.com"],
      "total_aed": "185,600.50",
      "tag_added": true
    }
  ]
}
```

## Setting Up Kommo Webhook

### Option 1: Manual Trigger
Call the webhook endpoint manually when you want to process leads.

### Option 2: Scheduled (via cron or external service)
Set up a cron job or external service to call the webhook periodically:

```bash
# Every 5 minutes
*/5 * * * * curl -X POST "https://your-domain.com/webhook/generate-proforma?token=your-webhook-token"
```

### Option 3: Kommo Automation (Future)
Configure Kommo to call the webhook when:
- A lead enters the "Generate pro forma" status
- A button is clicked in the lead interface

## Security

- The webhook uses a separate `WEBHOOK_TOKEN` for validation
- Token is passed as a query parameter: `?token=xxx`
- Invalid tokens return 401 Unauthorized
- Keep your webhook token secure and different from `API_SECRET_TOKEN`

## Lead Processing Logic

```
1. Fetch all leads in "Generate pro forma" status
2. Filter out leads with "proforma" tag
3. Take first 3 leads
4. For each lead:
   - Fetch contact details
   - Fetch product catalog elements
   - Build proforma invoice JSON
   - Generate PDF
   - Email to customer
   - Save to MongoDB
   - Add "proforma" tag
```

## Error Handling

Leads may be skipped for these reasons:
- Missing contact information
- No email address
- No products in catalog
- Failed to fetch product details

Skipped leads will NOT receive the "proforma" tag and will be processed in the next webhook call.

## Monitoring

Check the logs for processing details:

```bash
# If using PM2
pm2 logs invoice-api

# Or check the service logs
journalctl -u invoice-api -f
```

## Troubleshooting

### Webhook returns "No leads to process"
- Check that leads exist in the "Generate pro forma" status
- Verify the status ID is 94720975
- Ensure KOMMO_SUBDOMAIN and KOMMO_ACCESS_TOKEN are correct

### Leads are skipped
- Check logs for specific error messages
- Verify lead has contact with email
- Ensure products are added to the lead

### Emails not sending
- Verify RESEND_API_KEY is valid
- Check FROM_EMAIL is configured
- Look for email sending errors in logs

### Tags not added
- Verify Kommo access token has write permissions
- Check network connectivity to Kommo API
- Leads will still be processed even if tagging fails

