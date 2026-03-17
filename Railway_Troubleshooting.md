# Railway Deployment Troubleshooting

Solutions for common issues when deploying Gelonghui News Scraper to Railway.

## 🔧 Permission Denied Error (Fixed)

**Error**: `exec container process '/root/.local/bin/streamlit': Permission denied`

**Solution**: ✅ **Already Fixed in Dockerfile**

The Dockerfile has been updated with:
```dockerfile
# Fix permissions for .local/bin executables
RUN chmod +x /root/.local/bin/*
```

**If you still see this error:**
1. **Redeploy your application** on Railway
2. Railway will rebuild the container with the fixed permissions
3. The error should be resolved

## 🚀 Redeployment Steps

### Option 1: Manual Redeploy
1. Go to Railway dashboard
2. Select your project
3. Click "Deploy" → "Redeploy"
4. Wait for deployment to complete

### Option 2: Trigger Redeploy via GitHub
1. Make a small change to any file (like adding a comment)
2. Commit and push to GitHub
3. Railway will automatically redeploy

### Option 3: Restart Services
1. Go to Railway dashboard
2. Select each service (Scraper, Web Dashboard)
3. Click "Restart" for each service

## 🧪 Testing After Fix

### Test Web Dashboard
1. Visit your web dashboard URL
2. Should load without permission errors
3. Check for Streamlit interface

### Test Database Connection
```bash
# In Railway console for Scraper service
python main.py test --database
```

### Test Scraping Service
```bash
# In Railway console for Scraper service
python main.py run --scraper --test
```

## 📊 Service Status Check

### Check Service Health
1. Go to Railway dashboard
2. Look for green checkmarks on services
3. Red X indicates issues

### View Service Logs
1. Click on any service
2. Go to "Logs" tab
3. Look for error messages

### Check Container Status
1. Click on service
2. Check "Container" status
3. Should show "Running"

## 🔍 Common Issues & Solutions

### Issue 1: Services Won't Start
**Symptoms**: Services show "Failed" or "Crashed"

**Solutions**:
1. Check logs for specific error messages
2. Verify environment variables are set
3. Redeploy the application
4. Check `railway.json` configuration

### Issue 2: Database Connection Failed
**Symptoms**: Database tests fail

**Solutions**:
1. Verify PostgreSQL service is running
2. Check `DATABASE_URL` environment variable
3. Run `python main.py setup` to initialize database
4. Check database connection in Railway console

### Issue 3: Web Dashboard Not Loading
**Symptoms**: Dashboard URL shows error or timeout

**Solutions**:
1. Check if Web Dashboard service is running
2. Verify port 8501 is exposed
3. Check Streamlit is accessible
4. Look for permission errors in logs

### Issue 4: Scraping Not Working
**Symptoms**: No data being collected

**Solutions**:
1. Check API connectivity
2. Verify scraping interval is set
3. Check logs for API errors
4. Test scraping manually with `--test` flag

## 🛠️ Manual Recovery Steps

### Complete Reset (Last Resort)
If nothing works, try a complete reset:

1. **Delete Project on Railway**
   - Go to Railway dashboard
   - Delete the entire project

2. **Redeploy from GitHub**
   - Go to railway.app
   - Deploy from GitHub repo again
   - Select `Antiant888/livestream`

3. **Reconfigure Database**
   - Add PostgreSQL database
   - Run setup script: `python railway_setup.py`

4. **Verify Everything Works**
   - Test all services
   - Check web dashboard
   - Verify scraping

## 📞 Getting Help

### Check Logs First
Always check service logs in Railway dashboard before asking for help.

### Common Log Messages
- `Permission denied`: Fixed in Dockerfile
- `Connection refused`: Database or service issues
- `Module not found`: Missing dependencies
- `API error`: External API issues

### When to Ask for Help
- Logs show unclear error messages
- Multiple troubleshooting steps failed
- Deployment consistently fails

## ✅ Success Indicators

After fixing the permission issue, you should see:

1. ✅ **Services Running**: Both Scraper and Web Dashboard show green status
2. ✅ **Web Dashboard Loading**: URL loads Streamlit interface
3. ✅ **Database Connected**: Database tests pass
4. ✅ **Scraping Active**: Logs show successful data collection
5. ✅ **No Permission Errors**: No more "Permission denied" messages

## 🎉 You're All Set!

The permission issue has been resolved. Your Gelonghui News Scraper should now deploy successfully on Railway with:

- ✅ PostgreSQL database
- ✅ Working web dashboard
- ✅ Active scraping service
- ✅ No permission errors

**Next Steps**:
1. Redeploy your application
2. Test all services
3. Visit your web dashboard
4. Monitor the scraping activity

Your project is ready for production use! 🌟