# MongoDB Integration for Proforma Invoices

## Overview

The Invoice API now includes MongoDB integration to track and manage proforma invoices by deal number. Before generating a proforma invoice, the system checks if a record with the same deal number exists in the database and either updates the existing record or creates a new one.

## Features

- **Automatic Upsert**: When generating a proforma invoice, the system automatically:
  - Checks if a deal number exists in the database
  - Updates the existing record if found
  - Creates a new record if not found
  
- **Deal Number Tracking**: Every proforma invoice is uniquely identified by its deal number
- **Audit Trail**: Each record includes `created_at` and `updated_at` timestamps

## Environment Variables

Add the following environment variables to your `.env` file:

```bash
# MongoDB Configuration
MONGO_INITDB_ROOT_USERNAME=mongo
MONGO_INITDB_ROOT_PASSWORD=gRXyUShRLEXknyvTSgwxjhzuoydOPCjp

# For Railway deployment (use Railway variables):
MONGO_PUBLIC_URL=mongodb://${MONGO_INITDB_ROOT_USERNAME}:${MONGO_INITDB_ROOT_PASSWORD}@${RAILWAY_TCP_PROXY_DOMAIN}:${RAILWAY_TCP_PROXY_PORT}
MONGO_URL=mongodb://${MONGO_INITDB_ROOT_USERNAME}:${MONGO_INITDB_ROOT_PASSWORD}@${RAILWAY_PRIVATE_DOMAIN}:27017

# For local development:
MONGO_URL=mongodb://mongo:gRXyUShRLEXknyvTSgwxjhzuoydOPCjp@localhost:27017
MONGOHOST=localhost
MONGOPORT=27017
MONGOUSER=mongo
MONGOPASSWORD=gRXyUShRLEXknyvTSgwxjhzuoydOPCjp
```

## Database Structure

### Database: `invoices_db`
### Collection: `proforma_invoices`

Each document contains:
- **deal_number** (string, indexed): Unique identifier for the deal
- **invoice**: Invoice information including number, date, and deal number
- **issued_to**: Customer information
- **terms**: Payment terms and conditions
- **items**: Array of invoice line items
- **amount_in_words**: Total amount in words
- **created_at** (datetime): When the record was first created
- **updated_at** (datetime): When the record was last updated

## API Changes

### Proforma Invoice Request

The proforma invoice request now **requires** a `deal_number` field in the invoice object:

```json
{
  "invoice": {
    "number": "00PI25-00000002",
    "date_of_issuing": "October 12, 2025",
    "deal_number": "12342231890"  // REQUIRED
  },
  "issued_to": { ... },
  "terms": { ... },
  "items": [ ... ],
  "amount_in_words": "...",
  "recipient_emails": [ ... ]
}
```

### API Response

The response now includes MongoDB operation details:

```json
{
  "status": "success",
  "message": "Proforma invoice generated and sent successfully",
  "invoice_number": "00PI25-00000002",
  "deal_number": "12342231890",
  "database_operation": "created",  // or "updated"
  "database_record_id": "507f1f77bcf86cd799439011",
  "pdf_filename": "ProformaInvoice_00PI25-00000002.pdf",
  "pdf_size_kb": 125.45,
  "emails_sent_to": ["customer@example.com"],
  "total_aed": "37,920.00"
}
```

## Installation

1. **Install MongoDB** (if not already installed):
   ```bash
   # Using Docker
   docker run -d \
     --name mongodb \
     -p 27017:27017 \
     -e MONGO_INITDB_ROOT_USERNAME=mongo \
     -e MONGO_INITDB_ROOT_PASSWORD=gRXyUShRLEXknyvTSgwxjhzuoydOPCjp \
     mongo:latest
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables** in `.env` file (see above)

4. **Start the API**:
   ```bash
   python main.py
   ```

## Usage Example

```bash
curl -X POST "http://localhost:8000/generate-proforma-invoice" \
  -H "Authorization: Bearer your-secret-token" \
  -H "Content-Type: application/json" \
  -d @sample_proforma_request.json
```

## MongoDB Helper Functions

The `mongodb_helper.py` module provides the following functions:

- **`find_by_deal_number(deal_number)`**: Find an invoice by deal number
- **`insert_invoice(invoice_data)`**: Insert a new invoice record
- **`update_invoice(deal_number, invoice_data)`**: Update an existing invoice
- **`upsert_invoice(deal_number, invoice_data)`**: Insert or update based on existence

## Behavior

### First Time (New Deal Number)
1. API receives proforma invoice request with deal number "12342231890"
2. System checks MongoDB for existing record with this deal number
3. No record found → Creates new document
4. Generates and sends PDF invoice
5. Returns response with `"database_operation": "created"`

### Subsequent Times (Existing Deal Number)
1. API receives proforma invoice request with deal number "12342231890"
2. System checks MongoDB for existing record with this deal number
3. Record found → Updates existing document with new data
4. Generates and sends PDF invoice
5. Returns response with `"database_operation": "updated"`

## Error Handling

If MongoDB connection fails:
- The API will return a 500 error
- Check logs for connection details
- Verify environment variables are set correctly
- Ensure MongoDB is running and accessible

## Security Notes

- MongoDB credentials are stored in environment variables
- Use Railway's private network URL (`RAILWAY_PRIVATE_DOMAIN`) for production
- Never commit `.env` file to version control
- Use `.env.example` as a template

## Troubleshooting

### Connection Errors
```
❌ Failed to connect to MongoDB: ...
```
**Solution**: Verify MongoDB is running and credentials are correct

### Authentication Errors
```
❌ MongoDB query error: Authentication failed
```
**Solution**: Check `MONGOUSER` and `MONGOPASSWORD` environment variables

### Database Not Found
MongoDB will automatically create the database and collection on first use.

## Monitoring

Check logs for MongoDB operations:
- `✓ Connected to MongoDB successfully`
- `✓ Found existing invoice for deal number: ...`
- `ℹ No existing invoice found for deal number: ...`
- `✓ Inserted new invoice with ID: ...`
- `✓ Updated invoice for deal number: ...`

