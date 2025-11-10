# Railway Deployment Guide

Complete guide for deploying the Invoice API with MongoDB to Railway.

## 🚀 Quick Deploy

### Prerequisites
- Railway account (sign up at https://railway.app)
- GitHub repository (recommended) or Railway CLI
- Your API tokens (Resend API key, etc.)

## Step-by-Step Deployment

### 1. Create New Railway Project

1. Go to https://railway.app
2. Click "New Project"
3. Choose deployment method:
   - **Option A**: Deploy from GitHub (recommended)
   - **Option B**: Deploy with Railway CLI

### 2. Add MongoDB Service

1. In your Railway project dashboard, click "New"
2. Select "Database" → "MongoDB"
3. Railway will automatically create a MongoDB instance with these variables:
   - `MONGO_INITDB_ROOT_USERNAME`
   - `MONGO_INITDB_ROOT_PASSWORD`
   - `MONGOHOST` (mapped to `RAILWAY_PRIVATE_DOMAIN`)
   - `MONGOPORT`
   - `RAILWAY_PRIVATE_DOMAIN`
   - `RAILWAY_TCP_PROXY_DOMAIN`
   - `RAILWAY_TCP_PROXY_PORT`

### 3. Add Invoice API Service

#### Option A: Deploy from GitHub (Recommended)

1. Push your code to GitHub:
   ```bash
   git add .
   git commit -m "Add MongoDB integration and Railway config"
   git push origin main
   ```

2. In Railway dashboard:
   - Click "New" → "GitHub Repo"
   - Select your repository
   - Railway will auto-detect Python and deploy

#### Option B: Deploy with Railway CLI

1. Install Railway CLI:
   ```bash
   npm i -g @railway/cli
   ```

2. Login and initialize:
   ```bash
   railway login
   railway init
   ```

3. Deploy:
   ```bash
   railway up
   ```

### 4. Configure Environment Variables

In your Railway project → Invoice API service → Variables tab, add:

```bash
# Required Variables
API_SECRET_TOKEN=your-secure-secret-token-here
RESEND_API_KEY=your-resend-api-key-here
FROM_EMAIL=invoices@yourdomain.com

# MongoDB Connection (Railway handles this automatically with service references)
# Option 1: Use Railway's service reference (recommended)
# Just ensure your MongoDB service is in the same project

# Option 2: Manual configuration
MONGO_URL=mongodb://${{MongoDB.MONGO_INITDB_ROOT_USERNAME}}:${{MongoDB.MONGO_INITDB_ROOT_PASSWORD}}@${{MongoDB.RAILWAY_PRIVATE_DOMAIN}}:27017
```

**Note**: Railway automatically injects MongoDB variables when services are in the same project. The code will use these automatically.

### 5. Configure Service Settings

In Railway dashboard → Invoice API service → Settings:

- **Start Command**: Already configured in `railway.toml` and `Procfile`
- **Build Command**: Automatic (uses nixpacks)
- **Port**: Railway auto-detects from `$PORT`

### 6. Deploy and Test

1. Railway will automatically deploy
2. Wait for deployment to complete (check "Deployments" tab)
3. Get your public URL from the "Settings" → "Domains" section
4. Click "Generate Domain" if no domain exists

### 7. Test Your Deployment

```bash
# Health check
curl https://your-app.railway.app/health

# Test token
curl -X POST https://your-app.railway.app/test-token \
  -H "Authorization: Bearer your-secret-token"

# Generate proforma invoice
curl -X POST https://your-app.railway.app/generate-proforma-invoice \
  -H "Authorization: Bearer your-secret-token" \
  -H "Content-Type: application/json" \
  -d @sample_proforma_request.json
```

## 🔧 Configuration Files

The following files are configured for Railway deployment:

### `railway.toml`
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10
```

### `Procfile`
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### `nixpacks.toml`
Configures system dependencies for WeasyPrint (PDF generation):
- Python 3.10
- Cairo, Pango, GDK-Pixbuf (for PDF rendering)
- libffi, gobject-introspection

## 📊 Railway Services Architecture

```
┌─────────────────────────────────────────────┐
│           Railway Project                   │
│                                             │
│  ┌──────────────────┐  ┌────────────────┐  │
│  │   Invoice API    │  │   MongoDB      │  │
│  │   (Python)       │──│   (Database)   │  │
│  │                  │  │                │  │
│  │  Port: $PORT     │  │  Port: 27017   │  │
│  │  Public Domain   │  │  Private only  │  │
│  └──────────────────┘  └────────────────┘  │
│           │                                 │
│           │ RAILWAY_PRIVATE_DOMAIN          │
│           │ (Internal Network)              │
└───────────┼─────────────────────────────────┘
            │
            │ Public Internet
            ▼
      Your API Users
```

## 🔐 Environment Variables Reference

### Automatically Provided by Railway (MongoDB Service)

```bash
MONGO_INITDB_ROOT_USERNAME    # MongoDB admin username
MONGO_INITDB_ROOT_PASSWORD    # MongoDB admin password
MONGOHOST                     # MongoDB host (RAILWAY_PRIVATE_DOMAIN)
MONGOPORT                     # MongoDB port (27017)
RAILWAY_PRIVATE_DOMAIN        # Internal network domain
RAILWAY_TCP_PROXY_DOMAIN      # External TCP proxy (if needed)
RAILWAY_TCP_PROXY_PORT        # External TCP proxy port
```

### You Must Provide

```bash
API_SECRET_TOKEN              # Your API authentication token
RESEND_API_KEY                # Your Resend email API key
FROM_EMAIL                    # Sender email address
```

### Optional (Auto-constructed if not provided)

```bash
MONGO_URL                     # Full MongoDB connection string
MONGOUSER                     # MongoDB username (fallback)
MONGOPASSWORD                 # MongoDB password (fallback)
```

## 🔍 Connection String Priority

The `mongodb_helper.py` uses this priority:

1. **`MONGO_URL`** (if set) - direct connection string
2. **Constructed from components**:
   - Uses `MONGOHOST`, `MONGOPORT`, `MONGOUSER`, `MONGOPASSWORD`
   - Railway provides these automatically

## 🎯 Connecting Services in Railway

### Automatic Connection (Recommended)

Railway automatically connects services in the same project:

1. Both services exist in the same project
2. Variables are auto-injected
3. Uses private network (faster & secure)
4. No manual configuration needed

### Manual Connection

If you need to manually connect:

1. Go to MongoDB service → Variables
2. Copy the private URL: `mongodb://${{...}}`
3. Add to Invoice API service variables as `MONGO_URL`

## 📝 Deployment Checklist

- [ ] Code pushed to GitHub (or ready for CLI deploy)
- [ ] Railway project created
- [ ] MongoDB service added to project
- [ ] Invoice API service deployed
- [ ] Environment variables configured:
  - [ ] `API_SECRET_TOKEN`
  - [ ] `RESEND_API_KEY`
  - [ ] `FROM_EMAIL`
- [ ] Domain generated for API service
- [ ] Health check passes
- [ ] Test API endpoints working
- [ ] MongoDB connection successful
- [ ] Email sending working (test invoice)

## 🐛 Troubleshooting

### Build Failures

**Error**: Missing system dependencies for WeasyPrint

**Solution**: Ensure `nixpacks.toml` exists with required packages:
```toml
[phases.setup]
nixPkgs = ["python310", "cairo", "pango", "gdk-pixbuf", "libffi", "gobject-introspection"]
```

### MongoDB Connection Errors

**Error**: `Connection refused` or `Authentication failed`

**Solutions**:
1. Check both services are in the same Railway project
2. Verify MongoDB service is running (check status)
3. Check variables are injected: Railway dashboard → Service → Variables
4. Look at deployment logs for connection details

### Application Crashes

**Error**: Application keeps restarting

**Solutions**:
1. Check logs: Railway dashboard → Service → Deployments → View Logs
2. Verify all required environment variables are set
3. Check `requirements.txt` has all dependencies
4. Ensure `PORT` variable is used correctly

### Import Errors

**Error**: `ModuleNotFoundError`

**Solution**: 
1. Ensure all dependencies in `requirements.txt`
2. Railway uses `pip install -r requirements.txt`
3. Check deployment logs for install errors

## 📊 Monitoring & Logs

### View Logs

1. Railway dashboard → Your service
2. Click "Deployments" tab
3. Click on latest deployment
4. Click "View Logs"

### Key Log Messages

```
✓ Connected to MongoDB successfully
📄 Generating proforma invoice: ...
✓ Created new database record for deal number: ...
✓ Updated existing database record for deal number: ...
📝 Generating HTML...
📄 Converting to PDF...
📧 Sending to: customer@example.com
✓ Email sent to customer@example.com
```

### Metrics

Railway provides:
- CPU usage
- Memory usage
- Network traffic
- Request count
- Response times

## 🔄 Updates & Redeployment

### Auto-Deploy (GitHub)

If connected to GitHub:
1. Push changes to main branch
2. Railway automatically redeploys
3. Zero-downtime deployment

### Manual Deploy (CLI)

```bash
railway up
```

### Rollback

1. Railway dashboard → Service → Deployments
2. Find previous successful deployment
3. Click three dots → "Redeploy"

## 💰 Pricing

Railway offers:
- **Free Tier**: $5 credit/month, limited resources
- **Hobby Plan**: $5/month base + usage
- **Pro Plan**: $20/month base + usage

### Estimated Costs

For typical invoice API usage:
- **API Service**: ~$5-10/month
- **MongoDB**: ~$5-10/month
- **Total**: ~$10-20/month

## 🔒 Security Best Practices

1. **Use Private Network**
   - MongoDB communicates via `RAILWAY_PRIVATE_DOMAIN`
   - Never expose MongoDB to public internet

2. **Secure API Token**
   - Generate strong `API_SECRET_TOKEN`
   - Don't commit to Git

3. **Environment Variables**
   - All secrets in Railway variables
   - Never in code

4. **HTTPS**
   - Railway provides SSL by default
   - All traffic encrypted

## 📚 Additional Resources

- Railway Documentation: https://docs.railway.app
- Railway MongoDB Guide: https://docs.railway.app/databases/mongodb
- Railway Python Guide: https://docs.railway.app/languages/python
- Nixpacks: https://nixpacks.com

## 🆘 Support

- Railway Discord: https://discord.gg/railway
- Railway Status: https://status.railway.app
- GitHub Issues: Your repository

## ✅ Success Indicators

Your deployment is successful when:

1. ✅ Service shows "Active" status
2. ✅ Health check returns `{"status": "ok"}`
3. ✅ MongoDB connection logs appear
4. ✅ Test invoice generates and sends
5. ✅ MongoDB stores the record
6. ✅ No error logs in deployment

---

**Deployment Status**: Ready for Railway  
**Last Updated**: November 10, 2025  
**Configuration Files**: railway.toml, Procfile, nixpacks.toml, .env.example

