# Railway Deployment Guide

Complete step-by-step guide to deploy your Gelonghui News Scraper to Railway with PostgreSQL database.

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- GitHub account with the repository: https://github.com/Antiant888/livestream
- Railway account: [railway.app](https://railway.app)

## 📋 Step-by-Step Deployment

### Step 1: Connect GitHub Repository to Railway

1. **Go to Railway**: Visit [railway.app](https://railway.app) and sign in with your GitHub account
2. **Connect Repository**:
   - Click "Deploy from GitHub Repo"
   - Select your repository: `Antiant888/livestream`
   - Click "Deploy"

### Step 2: Configure Environment Variables

Railway will automatically detect the `railway.json` configuration file and set up the services. You need to configure these environment variables:

#### **Required Environment Variables**
1. **DATABASE_URL** (PostgreSQL connection string)
   - Railway automatically creates this when you add PostgreSQL
   - Format: `postgresql://username:password@host:port/database`

2. **SCRAPING_INTERVAL_MINUTES** (Optional)
   - Default: `1` (scrape every 1 minute)
   - Set to your preferred interval (e.g., `5` for every 5 minutes)

3. **LOG_LEVEL** (Optional)
   - Default: `INFO`
   - Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`

#### **To Add Environment Variables:**
1. In Railway dashboard, go to your project
2. Click "Settings" → "Environment Variables"
3. Add the variables above

### Step 3: Add PostgreSQL Database

1. **In Railway Dashboard**:
   - Go to your project
   - Click "New" → "Database"
   - Select "PostgreSQL"
   - Click "Deploy"

2. **Database Configuration**:
   - Railway automatically creates a PostgreSQL instance
   - The `DATABASE_URL` environment variable is automatically set
   - No manual configuration needed!

### Step 4: Configure Services

Your `railway.json` file defines two services:

#### **Service 1: Scraper**
- **Command**: `python main.py run --scraper --interval 1`
- **Purpose**: Runs the scraping service as a daemon
- **Auto-start**: Yes (runs continuously)

#### **Service 2: Web Dashboard**
- **Command**: `python main.py run --dashboard`
- **Purpose**: Runs the Streamlit web dashboard
- **Port**: 8501
- **Auto-start**: Yes

### Step 5: Initialize Database

After deployment, you need to initialize the database:

1. **Open Railway Console**:
   - Go to your project in Railway
   - Click on the "Scraper" service
   - Click "Open Console" or "SSH"

2. **Run Database Setup**:
   ```bash
   python main.py setup
   ```

3. **Verify Database**:
   ```bash
   python main.py test --database
   ```

### Step 6: Start Services

1. **Start Scraper Service**:
   - In Railway dashboard, go to "Scraper" service
   - Click "Start" (should auto-start after deployment)

2. **Start Web Dashboard**:
   - In Railway dashboard, go to "Web Dashboard" service
   - Click "Start" (should auto-start after deployment)

## 🎯 Service URLs

After deployment, you'll get:

### **Web Dashboard URL**
- Format: `https://your-project-name.up.railway.app`
- This is your Streamlit dashboard
- Access real-time analytics and visualizations

### **Scraper Service**
- Runs in background
- Automatically scrapes data based on interval
- Logs available in Railway dashboard

## 🔧 Manual Configuration (If Needed)

### **If Services Don't Start Automatically**

1. **Check Service Configuration**:
   - Go to Railway dashboard
   - Click on each service
   - Verify the command is correct

2. **Manual Service Setup**:
   - **Scraper Service**:
     - Command: `python main.py run --scraper --interval 1`
     - Port: Not required (daemon service)
   - **Web Dashboard**:
     - Command: `python main.py run --dashboard`
     - Port: `8501`

### **Environment Variables Setup**

If environment variables aren't set automatically:

1. **Get Database URL**:
   - Go to PostgreSQL service in Railway
   - Copy the connection string
   - Set as `DATABASE_URL` environment variable

2. **Set Other Variables**:
   ```bash
   # In Railway environment variables:
   SCRAPING_INTERVAL_MINUTES=1
   LOG_LEVEL=INFO
   ```

## 🧪 Testing Your Deployment

### **Test Database Connection**
```bash
# In Railway console for Scraper service
python main.py test --database
```

### **Test API Connection**
```bash
# In Railway console for Scraper service
python main.py test --api
```

### **Test Web Dashboard**
1. Visit your web dashboard URL
2. Check if the dashboard loads
3. Verify data is being displayed

### **Test Scraping**
```bash
# In Railway console for Scraper service
python main.py run --scraper --interval 1 --test
```

## 📊 Monitoring and Maintenance

### **View Logs**
1. Go to Railway dashboard
2. Click on any service
3. View real-time logs
4. Monitor scraping activity and errors

### **Check Database**
1. Go to PostgreSQL service
2. View connection details
3. Monitor database size and performance

### **Service Health**
- Railway automatically monitors service health
- Services auto-restart if they crash
- View uptime and performance metrics

## 🔧 Troubleshooting

### **Common Issues**

#### **1. Database Connection Failed**
```bash
# Check DATABASE_URL is set correctly
echo $DATABASE_URL

# Test connection
python main.py test --database
```

#### **2. Services Won't Start**
```bash
# Check logs for errors
# In Railway console, check service logs

# Verify requirements.txt
pip install -r requirements.txt
```

#### **3. Web Dashboard Not Loading**
- Check if port 8501 is exposed
- Verify Streamlit is running
- Check environment variables

#### **4. Scraping Not Working**
- Check API connectivity
- Verify scraping interval
- Check logs for errors

### **Getting Help**
1. Check Railway logs for error messages
2. Run test commands in Railway console
3. Verify environment variables
4. Check `docs/TROUBLESHOOTING.md` for more help

## 🚀 Advanced Configuration

### **Custom Scraping Interval**
Edit environment variable:
```bash
SCRAPING_INTERVAL_MINUTES=5  # Scrape every 5 minutes
```

### **Custom Database**
If using external PostgreSQL:
```bash
DATABASE_URL=postgresql://user:pass@host:port/db
```

### **Multiple Environments**
- **Development**: Use Railway's staging environment
- **Production**: Use Railway's production environment
- Configure different settings for each

## 📈 Performance Optimization

### **Database Optimization**
- Railway PostgreSQL is already optimized
- Monitor database size and scale if needed
- Use Railway's performance monitoring

### **Service Scaling**
- Railway automatically scales based on traffic
- Monitor resource usage in dashboard
- Upgrade plan if needed for high traffic

## 🎉 Success!

Your Gelonghui News Scraper is now deployed on Railway with:
- ✅ PostgreSQL database
- ✅ Automated scraping service
- ✅ Streamlit web dashboard
- ✅ Real-time data processing
- ✅ Professional deployment

### **Next Steps:**
1. Visit your web dashboard URL
2. Monitor the scraping service
3. Check the data being collected
4. Share your project with others!

Your project is now live and ready for production use! 🌟