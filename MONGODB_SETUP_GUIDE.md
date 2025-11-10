# MongoDB Setup Guide

This guide will help you set up MongoDB integration for the Invoice API.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install `pymongo==4.6.1` along with other dependencies.

### 2. Set Up MongoDB

#### Option A: Using Docker (Recommended)

```bash
docker run -d \
  --name mongodb-invoices \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=mongo \
  -e MONGO_INITDB_ROOT_PASSWORD=gRXyUShRLEXknyvTSgwxjhzuoydOPCjp \
  -v mongodb_data:/data/db \
  mongo:latest
```

#### Option B: Local MongoDB Installation

1. Download and install MongoDB from https://www.mongodb.com/try/download/community
2. Start MongoDB service
3. Create user with authentication

#### Option C: Railway Deployment

If deploying to Railway:
1. Add MongoDB service to your project
2. Railway will automatically provide the environment variables
3. Use the Railway-specific connection string format

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy from example
cp .env.example .env

# Edit .env with your values
```

For local development, your `.env` should look like:

```env
# API Configuration
API_SECRET_TOKEN=your-secret-token-here

# Email Configuration
RESEND_API_KEY=your-resend-api-key-here
FROM_EMAIL=invoices@yourdomain.com

# MongoDB Configuration (Local)
MONGO_URL=mongodb://mongo:gRXyUShRLEXknyvTSgwxjhzuoydOPCjp@localhost:27017
MONGOHOST=localhost
MONGOPORT=27017
MONGOUSER=mongo
MONGOPASSWORD=gRXyUShRLEXknyvTSgwxjhzuoydOPCjp
```

For Railway deployment:

```env
# MongoDB Configuration (Railway)
MONGO_URL=mongodb://${MONGO_INITDB_ROOT_USERNAME}:${MONGO_INITDB_ROOT_PASSWORD}@${RAILWAY_PRIVATE_DOMAIN}:27017
MONGOHOST=${RAILWAY_PRIVATE_DOMAIN}
MONGOPORT=27017
MONGOUSER=${MONGO_INITDB_ROOT_USERNAME}
MONGOPASSWORD=${MONGO_INITDB_ROOT_PASSWORD}
```

### 4. Test MongoDB Connection

```bash
python test_mongodb.py
```

Expected output:
```
============================================================
MongoDB Integration Test
============================================================
🔍 Testing MongoDB connection...
🔌 Connecting to MongoDB...
✓ Connected to MongoDB successfully
✓ Successfully connected to MongoDB!

🔍 Testing find operation...
ℹ No existing test record found
✓ Correctly returned None for non-existent record

🔍 Testing upsert operation...
✓ Inserted new invoice with ID: 507f1f77bcf86cd799439011
✓ First upsert: Created (ID: 507f1f77bcf86cd799439011)
✓ Updated invoice for deal number: TEST123456
✓ Second upsert: Updated (ID: 507f1f77bcf86cd799439011)
✓ Retrieved record:
  - Deal Number: TEST123456
  - Invoice Number: TEST-001
  - Quantity: 2.0
  - Created At: 2025-11-10 12:34:56.789000
  - Updated At: 2025-11-10 12:34:58.123000

============================================================
✓ All tests completed!
============================================================
```

### 5. Start the API

```bash
python main.py
```

Or with PM2:
```bash
pm2 start ecosystem.config.js
```

## Testing the Integration

### Test with Sample Request

```bash
curl -X POST "http://localhost:8000/generate-proforma-invoice" \
  -H "Authorization: Bearer your-secret-token" \
  -H "Content-Type: application/json" \
  -d @sample_proforma_request.json
```

Expected response:
```json
{
  "status": "success",
  "message": "Proforma invoice generated and sent successfully",
  "invoice_number": "00PI25-00000002",
  "deal_number": "12342231890",
  "database_operation": "created",
  "database_record_id": "507f1f77bcf86cd799439011",
  "pdf_filename": "ProformaInvoice_00PI25-00000002.pdf",
  "pdf_size_kb": 125.45,
  "emails_sent_to": ["ivan.f@mxd.digital"],
  "total_aed": "37,920.00"
}
```

### Verify in MongoDB

Using MongoDB shell:
```bash
# Connect to MongoDB
docker exec -it mongodb-invoices mongosh -u mongo -p gRXyUShRLEXknyvTSgwxjhzuoydOPCjp

# In MongoDB shell:
use invoices_db
db.proforma_invoices.find({"deal_number": "12342231890"}).pretty()
```

Using MongoDB Compass:
1. Connect to `mongodb://mongo:gRXyUShRLEXknyvTSgwxjhzuoydOPCjp@localhost:27017`
2. Navigate to `invoices_db` → `proforma_invoices`
3. Filter by deal_number

## Troubleshooting

### Connection Refused

**Error**: `Connection refused to localhost:27017`

**Solution**:
- Check if MongoDB is running: `docker ps | grep mongodb-invoices`
- Start MongoDB: `docker start mongodb-invoices`

### Authentication Failed

**Error**: `Authentication failed`

**Solution**:
- Verify credentials in `.env` match MongoDB configuration
- Check `MONGOUSER` and `MONGOPASSWORD` environment variables

### Module Not Found: pymongo

**Error**: `ModuleNotFoundError: No module named 'pymongo'`

**Solution**:
```bash
pip install pymongo==4.6.1
```

### MongoDB Not Configured

**Error**: `MongoDB collection not initialized`

**Solution**:
- Ensure all MongoDB environment variables are set in `.env`
- Restart the API after updating environment variables

## MongoDB Collections

### Database: `invoices_db`

#### Collection: `proforma_invoices`

Structure:
```json
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "invoice": {
    "number": "00PI25-00000002",
    "date_of_issuing": "October 12, 2025",
    "deal_number": "12342231890"
  },
  "issued_to": {
    "name": "Diachuk Valeriia",
    "address": "450 Folsom street, 2409, San Francisco, CA, 94105",
    "trn": "",
    "email": "valsudilovskaya@gmail.com"
  },
  "terms": {
    "payment_terms": "Advance payment of 50% before Delivery",
    "amount_paid": "18960.00"
  },
  "items": [ ... ],
  "amount_in_words": "Thirty seven thousand nine hundred twenty AED ONLY",
  "created_at": ISODate("2025-11-10T12:34:56.789Z"),
  "updated_at": ISODate("2025-11-10T12:34:56.789Z")
}
```

## Security Best Practices

1. **Never commit `.env` file**
   - Already in `.gitignore`
   - Use `.env.example` as template

2. **Use strong passwords**
   - The example password is for development only
   - Use a strong, unique password in production

3. **Use private network in Railway**
   - Use `RAILWAY_PRIVATE_DOMAIN` for internal communication
   - Use `RAILWAY_TCP_PROXY_DOMAIN` for external access (if needed)

4. **Restrict API access**
   - Always use API token authentication
   - Change default `API_SECRET_TOKEN` to a secure value

## Backup and Recovery

### Backup MongoDB Data

```bash
# Using Docker
docker exec mongodb-invoices mongodump \
  --username mongo \
  --password gRXyUShRLEXknyvTSgwxjhzuoydOPCjp \
  --out /backup

# Copy backup to host
docker cp mongodb-invoices:/backup ./mongodb_backup
```

### Restore MongoDB Data

```bash
# Copy backup to container
docker cp ./mongodb_backup mongodb-invoices:/backup

# Restore
docker exec mongodb-invoices mongorestore \
  --username mongo \
  --password gRXyUShRLEXknyvTSgwxjhzuoydOPCjp \
  /backup
```

## Monitoring

### Check Logs

```bash
# API logs
tail -f logs/api.log

# MongoDB logs (Docker)
docker logs -f mongodb-invoices
```

### View Statistics

```javascript
// In MongoDB shell
use invoices_db

// Count documents
db.proforma_invoices.countDocuments()

// Find recent invoices
db.proforma_invoices.find().sort({"created_at": -1}).limit(10)

// Find by deal number
db.proforma_invoices.find({"deal_number": "12342231890"})

// Count by date
db.proforma_invoices.aggregate([
  {
    $group: {
      _id: "$invoice.date_of_issuing",
      count: { $sum: 1 }
    }
  }
])
```

## Next Steps

1. ✅ MongoDB installed and running
2. ✅ Environment variables configured
3. ✅ Dependencies installed
4. ✅ Connection tested
5. ✅ API running

You're all set! The invoice API will now automatically track proforma invoices in MongoDB.

