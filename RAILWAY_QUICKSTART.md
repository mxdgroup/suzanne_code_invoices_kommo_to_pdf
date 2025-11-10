# Railway Deployment - Quick Start

Deploy your Invoice API to Railway in 5 minutes.

## 🚀 One-Click Deploy Steps

### 1. Prepare Your Repository

```bash
# Ensure all files are committed
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

### 2. Deploy to Railway

#### Via Railway Dashboard

1. Go to https://railway.app
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository
5. Railway auto-deploys your API service

#### Via Railway CLI

```bash
# Install CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### 3. Add MongoDB

1. In Railway dashboard, click **"New"**
2. Select **"Database"** → **"MongoDB"**
3. MongoDB starts automatically
4. Variables auto-inject into your API service

### 4. Set Environment Variables

In Railway dashboard → Your API Service → Variables:

```env
API_SECRET_TOKEN=your-secure-token-here
RESEND_API_KEY=your-resend-key-here
FROM_EMAIL=invoices@yourdomain.com
```

**MongoDB variables are automatic!** ✅

### 5. Get Your URL

1. Railway dashboard → Your API Service → Settings
2. Under **"Domains"**, click **"Generate Domain"**
3. Your API URL: `https://your-app.railway.app`

### 6. Test It

```bash
# Replace with your Railway URL and token
export RAILWAY_URL="https://your-app.railway.app"
export API_TOKEN="your-secret-token"

# Health check
curl $RAILWAY_URL/health

# Test invoice generation
curl -X POST "$RAILWAY_URL/generate-proforma-invoice" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d @sample_proforma_request.json
```

## ✅ Success!

You should see:
- ✅ API returns `200 OK`
- ✅ PDF generated and emailed
- ✅ Record saved to MongoDB
- ✅ Response includes `database_operation: "created"`

## 📁 Required Files (Already Configured)

All these files are already in your repository:

- ✅ `railway.toml` - Railway configuration
- ✅ `Procfile` - Start command
- ✅ `nixpacks.toml` - Build dependencies
- ✅ `requirements.txt` - Python packages
- ✅ `.env.example` - Environment template
- ✅ `main.py` - FastAPI application
- ✅ `mongodb_helper.py` - Database operations

## 🔧 Environment Variables (Auto-Provided by Railway)

When you add MongoDB to Railway, these are automatic:

```env
MONGO_INITDB_ROOT_USERNAME  ← Auto
MONGO_INITDB_ROOT_PASSWORD  ← Auto
MONGOHOST                   ← Auto (RAILWAY_PRIVATE_DOMAIN)
MONGOPORT                   ← Auto (27017)
RAILWAY_PRIVATE_DOMAIN      ← Auto
```

**You only need to add:**
- `API_SECRET_TOKEN`
- `RESEND_API_KEY`
- `FROM_EMAIL`

## 📊 Project Structure in Railway

```
Your Railway Project
├── Invoice API Service    (your app)
│   ├── Environment: API_SECRET_TOKEN, RESEND_API_KEY, FROM_EMAIL
│   └── Domain: https://your-app.railway.app
└── MongoDB Service        (database)
    └── Private network: Auto-connected
```

## 🐛 Common Issues

### Build Fails
**Problem**: Missing WeasyPrint dependencies  
**Solution**: Already fixed in `nixpacks.toml` ✅

### MongoDB Connection Fails
**Problem**: Can't connect to database  
**Solution**: Ensure MongoDB service exists in same Railway project

### API Returns 500
**Problem**: Missing environment variables  
**Solution**: Add `API_SECRET_TOKEN`, `RESEND_API_KEY`, `FROM_EMAIL`

### PDF Generation Fails
**Problem**: WeasyPrint errors  
**Solution**: Check deployment logs, ensure nixpacks installed correctly

## 📝 Deployment Checklist

Before deploying, ensure:

- [ ] Code pushed to GitHub
- [ ] All environment variables ready:
  - [ ] API_SECRET_TOKEN
  - [ ] RESEND_API_KEY
  - [ ] FROM_EMAIL
- [ ] Test request JSON file ready (`sample_proforma_request.json`)

## 🎯 What Happens on Deploy

1. **Railway detects Python** (via `requirements.txt`)
2. **Nixpacks installs system packages** (cairo, pango, etc.)
3. **Pip installs Python packages** (`pip install -r requirements.txt`)
4. **Starts app** (`uvicorn main:app --host 0.0.0.0 --port $PORT`)
5. **Connects to MongoDB** (via private network)
6. **Ready to accept requests!** 🎉

## 💡 Pro Tips

1. **Use Private Network**: Railway auto-uses `RAILWAY_PRIVATE_DOMAIN` for MongoDB (faster & secure)

2. **Auto-Deploy**: Connect GitHub for automatic deploys on push

3. **View Logs**: Railway dashboard → Service → Deployments → View Logs

4. **Rollback**: If something breaks, redeploy previous version

5. **Monitoring**: Check CPU/Memory usage in Railway dashboard

## 📚 Need More Details?

See `RAILWAY_DEPLOYMENT.md` for:
- Detailed troubleshooting
- Security best practices
- Monitoring & logging
- Pricing information
- Advanced configuration

## 🆘 Quick Help

- **Can't connect to MongoDB?** → Check both services in same project
- **API returns 401?** → Check `API_SECRET_TOKEN` is set
- **Emails not sending?** → Verify `RESEND_API_KEY` is correct
- **Build fails?** → Check deployment logs for specific error

## 🌐 Your API is Live!

Once deployed, your API endpoints are:

- `GET /` - Health check
- `GET /health` - Detailed health
- `POST /test-token` - Test authentication
- `POST /generate-invoice` - Generate tax invoice
- `POST /generate-proforma-invoice` - Generate proforma invoice (with MongoDB)

---

**Total Time**: ~5 minutes  
**Difficulty**: Easy  
**Cost**: $10-20/month (after free trial)

