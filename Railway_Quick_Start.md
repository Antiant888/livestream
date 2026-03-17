# Railway Quick Start Guide

Quick reference for deploying and managing your Gelonghui News Scraper on Railway.

## 🚀 5-Minute Deployment

### Step 1: Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "Deploy from GitHub Repo"
4. Select: `Antiant888/livestream`
5. Click "Deploy"

### Step 2: Add PostgreSQL Database
1. In Railway dashboard, go to your project
2. Click "New" → "Database"
3. Select "PostgreSQL"
4. Click "Deploy"

### Step 3: Initialize Database
1. Go to "Scraper" service
2. Click "Open Console"
3. Run: `python railway_setup.py`

## 🔧 Essential Commands

### Database Management
```bash
# Initialize database
python main.py setup

# Test database connection
python main.py test --database

# View database status
python main.py status
```

### Scraping Management
```bash
# Start scraping (daemon mode)
python main.py run --scraper --interval 1

# Test scraping
python main.py run --scraper --test

# View scraping logs
# Check Railway dashboard → Scraper service → Logs
```

### Web Dashboard
```bash
# Start web dashboard
python main.py run --dashboard

# Dashboard URL: https://your-project-name.up.railway.app
```

### Testing Everything
```bash
# Run comprehensive setup and tests
python railway_setup.py

# Test individual components
python main.py test --api --database
```

## 📊 Service URLs

After deployment, you'll get:
- **Web Dashboard**: `https://your-project-name.up.railway.app`
- **Scraper Service**: Runs in background
- **Database**: PostgreSQL (managed by Railway)

## ⚙️ Environment Variables

Set these in Railway → Settings → Environment Variables:

```bash
DATABASE_URL=postgresql://... (auto-set by Railway)
SCRAPING_INTERVAL_MINUTES=1
LOG_LEVEL=INFO
```

## 🎯 Next Steps

1. **Visit Web Dashboard**: Check your analytics at the provided URL
2. **Monitor Logs**: Watch scraping activity in Railway dashboard
3. **Configure Interval**: Adjust `SCRAPING_INTERVAL_MINUTES` as needed
4. **Share Project**: Add to portfolio, share on social media

## 🆘 Quick Troubleshooting

### Database Connection Failed
```bash
# Check DATABASE_URL
echo $DATABASE_URL

# Re-run setup
python main.py setup
```

### Services Won't Start
```bash
# Check logs in Railway dashboard
# Verify environment variables
# Re-deploy if needed
```

### Web Dashboard Not Loading
- Check port 8501 is exposed
- Verify Streamlit is running
- Check environment variables

## 📈 Monitoring

### View Service Health
1. Go to Railway dashboard
2. Check service status indicators
3. View uptime and performance

### Check Database
1. Go to PostgreSQL service
2. Monitor connection details
3. Check database size and performance

### View Logs
1. Go to any service
2. Click "Logs" tab
3. Monitor real-time activity

## 🎉 Success!

Your Gelonghui News Scraper is now:
- ✅ Deployed on Railway
- ✅ Connected to PostgreSQL
- ✅ Running automated scraping
- ✅ Serving web dashboard
- ✅ Ready for production use

**Your project is live!** 🌟