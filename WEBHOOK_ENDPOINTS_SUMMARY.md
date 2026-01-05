# Invoice Webhook Endpoints - Quick Reference

## Overview

Two webhook endpoints for automatic invoice generation from Kommo leads:
1. **Proforma Invoice** - Initial invoice with deposit options
2. **Tax Invoice** - Final invoice with "Payment on Delivery"

---

## 1. Proforma Invoice Webhook

### Endpoint
```
POST /webhook/generate-proforma?token=YOUR_TOKEN
```

### Configuration
```python
# kommo_helper.py
GENERATE_PROFORMA_STATUS_ID = 94720975
```

### Invoice Format
- **Number:** `00PI25-00000001` (00PI25-{lead_id})
- **Title:** "PROFORMA INVOICE"
- **Payment Terms:** From lead's "Payment Terms" field
- **Deposit:** Uses "Deposit Amount" field if payment type is "Deposit"
- **Tag Added:** `proforma`

### Payment Terms Display
```
Terms and Conditions: {payment_terms} {deposit_amount} AED
```

Example: "Advance payment of 50% before Delivery **10000 AED**"

---

## 2. Tax Invoice Webhook

### Endpoint
```
POST /webhook/generate-tax-invoice?token=YOUR_TOKEN
```

### Configuration
```python
# kommo_helper.py
GENERATE_TAX_INVOICE_STATUS_ID = 94720977  # Update with your actual status ID
```

### Invoice Format
- **Number:** `TAXZS-00001` (TAXZS-{lead_id})
- **Title:** "TAX INVOICE"
- **Payment Terms:** "Payment on Delivery" (hardcoded)
- **Deposit:** Not shown (always 0)
- **Tag Added:** `tax_invoice`

### Payment Terms Display
```
Terms and Conditions: Payment on Delivery
```

---

## Common Features

### Both Endpoints:
✅ Use the same webhook token  
✅ Return 202 Accepted immediately  
✅ Process in background (up to 3 leads per call)  
✅ Skip leads already processed (check for tag)  
✅ Fetch data from Kommo (contacts, products, custom fields)  
✅ Apply discount from lead's "Discount" field  
✅ Generate PDF invoice  
✅ Send email with PDF attachment  
✅ Add tag to processed lead  

### Required Lead Data:
- ✅ Contact with email address
- ✅ At least one product from catalog
- ✅ Discount field (optional, defaults to 0%)
- ✅ Delivery address (recommended)

---

## Key Differences

| Feature | Proforma Invoice | Tax Invoice |
|---------|------------------|-------------|
| **Title** | PROFORMA INVOICE | TAX INVOICE |
| **Number Format** | 00PI25-{lead_id} | TAXZS-{lead_id} |
| **Payment Terms** | From Kommo field | "Payment on Delivery" |
| **Deposit Amount** | From Kommo field | Not shown |
| **Tag** | `proforma` | `tax_invoice` |
| **Status ID** | 94720975 | 94720977 |
| **Template** | `generate_proforma_invoice.py` | `generate_tax_invoice.py` |

---

## Setup Instructions

### 1. Configure Status IDs

Update `kommo_helper.py` with your actual status IDs:

```python
GENERATE_PROFORMA_STATUS_ID = 94720975  # Your proforma status ID
GENERATE_TAX_INVOICE_STATUS_ID = 94720977  # Your tax invoice status ID
```

### 2. Set Environment Variables

In `.env` file:

```env
KOMMO_SUBDOMAIN=yoursubdomain
KOMMO_ACCESS_TOKEN=your-access-token
WEBHOOK_TOKEN=your-webhook-token
RESEND_API_KEY=your-resend-api-key
FROM_EMAIL=invoices@yourdomain.com
```

### 3. Configure Kommo Webhooks

Add two webhooks in Kommo:

#### Proforma Invoice Webhook:
- **URL:** `https://your-domain.com/webhook/generate-proforma?token=your-webhook-token`
- **Trigger:** Lead status changed to "Generate pro forma"
- **Method:** POST

#### Tax Invoice Webhook:
- **URL:** `https://your-domain.com/webhook/generate-tax-invoice?token=your-webhook-token`
- **Trigger:** Lead status changed to "Generate tax invoice"
- **Method:** POST

---

## Testing

### Test Proforma Invoice:
```bash
curl -X POST "http://localhost:8000/webhook/generate-proforma?token=your-token"
```

### Test Tax Invoice:
```bash
curl -X POST "http://localhost:8000/webhook/generate-tax-invoice?token=your-token"
```

---

## Workflow Example

1. **Lead created** in Kommo with products and customer details
2. **Move to "Generate pro forma" status**
   - Webhook triggered → Proforma invoice generated and sent
   - Lead tagged with `proforma`
3. **Customer makes payment**
4. **Move to "Generate tax invoice" status**
   - Webhook triggered → Tax invoice generated and sent
   - Lead tagged with `tax_invoice`
5. **Done!** Both invoices stored in MongoDB and sent to customer

---

## Troubleshooting

### Leads not processed:
- ✅ Check webhook token is correct
- ✅ Verify status IDs match your Kommo settings
- ✅ Check logs for errors
- ✅ Ensure leads have required data (contact, products)
- ✅ Verify leads don't already have the tag

### Emails not sent:
- ✅ Check RESEND_API_KEY is valid
- ✅ Verify FROM_EMAIL is configured
- ✅ Check contact has valid email
- ✅ Review Resend dashboard for delivery status

### Wrong discount:
- ✅ Verify "Discount" field in Kommo has correct value
- ✅ Check discount extraction in logs
- ✅ Discount field should be: "5%", "10%", "15%", "20%", or "No Discount"

---

## Related Files

- `kommo_helper.py` - API integration and data preparation
- `generate_proforma_invoice.py` - Proforma invoice HTML template
- `generate_tax_invoice.py` - Tax invoice HTML template
- `main.py` - Webhook endpoints and background processing
- `convert_to_pdf.py` - HTML to PDF conversion
- `mongodb_helper.py` - Database storage for invoices

---

## Support

For issues or questions:
1. Check application logs
2. Review webhook execution in Kommo
3. Test endpoints manually with curl
4. Verify environment variables are set correctly

