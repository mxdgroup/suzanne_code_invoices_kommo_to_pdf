# MongoDB Integration - Quick Reference

## What Changed?

### 1. New Dependency
- Added `pymongo==4.6.1` to `requirements.txt`

### 2. New Files
- `mongodb_helper.py` - MongoDB connection and operations
- `test_mongodb.py` - Test script for MongoDB functionality
- `.env.example` - Environment variables template
- `MONGODB_INTEGRATION.md` - Full documentation
- `MONGODB_SETUP_GUIDE.md` - Setup instructions

### 3. Updated Files
- `main.py` - Added MongoDB integration to proforma invoice endpoint
- `sample_proforma_request.json` - Already includes `deal_number` field

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│  1. API receives proforma invoice request               │
│     with deal_number: "12342231890"                     │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  2. Check MongoDB for existing deal_number              │
└────────────┬────────────────────────────┬───────────────┘
             │                            │
    Found    │                            │  Not Found
             ▼                            ▼
┌─────────────────────┐      ┌──────────────────────────┐
│  3a. UPDATE         │      │  3b. CREATE              │
│  existing record    │      │  new record              │
└─────────┬───────────┘      └──────────┬───────────────┘
          │                             │
          └──────────┬──────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│  4. Generate HTML → PDF → Send Email                    │
└─────────────────────────────────────────────────────────┘
```

## Environment Variables (Add to .env)

```bash
# MongoDB
MONGO_URL=mongodb://mongo:gRXyUShRLEXknyvTSgwxjhzuoydOPCjp@localhost:27017
MONGOHOST=localhost
MONGOPORT=27017
MONGOUSER=mongo
MONGOPASSWORD=gRXyUShRLEXknyvTSgwxjhzuoydOPCjp
```

## Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start MongoDB (Docker)
docker run -d --name mongodb-invoices \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=mongo \
  -e MONGO_INITDB_ROOT_PASSWORD=gRXyUShRLEXknyvTSgwxjhzuoydOPCjp \
  mongo:latest

# 3. Configure .env
cp .env.example .env
# Edit .env with your values

# 4. Test connection
python test_mongodb.py

# 5. Start API
python main.py
```

## API Request (Now Requires deal_number)

```json
{
  "invoice": {
    "number": "00PI25-00000002",
    "date_of_issuing": "October 12, 2025",
    "deal_number": "12342231890"  ← REQUIRED
  },
  "issued_to": { ... },
  "terms": { ... },
  "items": [ ... ],
  "amount_in_words": "...",
  "recipient_emails": [ ... ]
}
```

## API Response (Now Includes MongoDB Info)

```json
{
  "status": "success",
  "invoice_number": "00PI25-00000002",
  "deal_number": "12342231890",           ← NEW
  "database_operation": "created",         ← NEW (or "updated")
  "database_record_id": "507f...",        ← NEW
  "pdf_filename": "ProformaInvoice_00PI25-00000002.pdf",
  "emails_sent_to": ["customer@example.com"],
  "total_aed": "37,920.00"
}
```

## MongoDB Commands

```javascript
// Connect
mongosh -u mongo -p gRXyUShRLEXknyvTSgwxjhzuoydOPCjp

// Use database
use invoices_db

// Find by deal number
db.proforma_invoices.find({"deal_number": "12342231890"})

// Count all invoices
db.proforma_invoices.countDocuments()

// Recent invoices
db.proforma_invoices.find().sort({"created_at": -1}).limit(10)
```

## Testing

```bash
# Test MongoDB connection
python test_mongodb.py

# Test API endpoint
curl -X POST "http://localhost:8000/generate-proforma-invoice" \
  -H "Authorization: Bearer your-secret-token" \
  -H "Content-Type: application/json" \
  -d @sample_proforma_request.json
```

## Common Operations

### Check if MongoDB is running
```bash
docker ps | grep mongodb-invoices
```

### Start MongoDB
```bash
docker start mongodb-invoices
```

### Stop MongoDB
```bash
docker stop mongodb-invoices
```

### View MongoDB logs
```bash
docker logs -f mongodb-invoices
```

### Backup MongoDB
```bash
docker exec mongodb-invoices mongodump \
  --username mongo \
  --password gRXyUShRLEXknyvTSgwxjhzuoydOPCjp \
  --out /backup
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| Connection refused | Start MongoDB: `docker start mongodb-invoices` |
| Authentication failed | Check credentials in `.env` |
| Module not found | Install: `pip install pymongo` |
| Collection not initialized | Verify environment variables are set |

## Files Structure

```
invoices_sc/
├── main.py                      # ← Updated (MongoDB integration)
├── mongodb_helper.py            # ← New (MongoDB operations)
├── test_mongodb.py              # ← New (Test script)
├── requirements.txt             # ← Updated (pymongo added)
├── .env.example                 # ← New (Environment template)
├── sample_proforma_request.json # Already has deal_number
├── MONGODB_INTEGRATION.md       # ← New (Full docs)
├── MONGODB_SETUP_GUIDE.md       # ← New (Setup guide)
└── MONGODB_QUICK_REFERENCE.md   # ← New (This file)
```

## What Happens When You Call the API?

1. **Request arrives** with deal_number in invoice object
2. **MongoDB checks** if deal_number exists
3. **If exists**: Updates the record with new data
4. **If not exists**: Creates new record
5. **Generates** HTML invoice
6. **Converts** HTML to PDF
7. **Sends** email with PDF attachment
8. **Returns** response including database operation status

## Key Points

✅ **Automatic**: No manual database operations needed  
✅ **Idempotent**: Same deal_number updates existing record  
✅ **Tracked**: Every record has created_at and updated_at  
✅ **Auditable**: Full history in MongoDB  
✅ **Secure**: Credentials in environment variables  

## Railway Deployment Notes

When deploying to Railway:

1. Add MongoDB service to your Railway project
2. Use these environment variables:
   ```
   MONGO_URL=mongodb://${MONGO_INITDB_ROOT_USERNAME}:${MONGO_INITDB_ROOT_PASSWORD}@${RAILWAY_PRIVATE_DOMAIN}:27017
   ```
3. Railway auto-populates: `RAILWAY_PRIVATE_DOMAIN`, `MONGO_INITDB_ROOT_USERNAME`, `MONGO_INITDB_ROOT_PASSWORD`
4. No changes needed to code!

## Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Start MongoDB: `docker run...`
3. ✅ Configure `.env` file
4. ✅ Test connection: `python test_mongodb.py`
5. ✅ Start API: `python main.py`
6. ✅ Test endpoint with sample request

Done! Your invoice API now tracks all proforma invoices in MongoDB.

