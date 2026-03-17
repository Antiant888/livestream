#!/usr/bin/env python3
"""
Railway Deployment Setup Script

This script helps with the initial setup of your Gelonghui News Scraper
on Railway, including database initialization and testing.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_environment():
    """Check if we're running in Railway environment"""
    railway_env = os.getenv('RAILWAY_ENVIRONMENT')
    if railway_env:
        print(f"✅ Railway environment detected: {railway_env}")
        return True
    else:
        print("⚠️  Not running in Railway environment")
        return False

def check_database_url():
    """Check if DATABASE_URL is set"""
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        print(f"✅ DATABASE_URL found: {db_url[:20]}...")
        return True
    else:
        print("❌ DATABASE_URL not set!")
        print("Please set DATABASE_URL in Railway environment variables")
        return False

def check_requirements():
    """Check if requirements are installed"""
    try:
        import sqlalchemy
        import requests
        import streamlit
        import apscheduler
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Installing requirements...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        return True

def setup_database():
    """Initialize the database"""
    print("🔧 Setting up database...")
    try:
        # Import after checking requirements
        from scraper.database import init_db
        init_db()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def test_database():
    """Test database connection"""
    print("🧪 Testing database connection...")
    try:
        from scraper.database import test_connection
        result = test_connection()
        if result:
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_api():
    """Test API connection"""
    print("🧪 Testing API connection...")
    try:
        from scraper.api_client import test_api_connection
        result = test_api_connection()
        if result:
            print("✅ API connection successful")
            return True
        else:
            print("❌ API connection failed")
            return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def run_initial_scrape():
    """Run initial data scrape"""
    print("🕷️  Running initial data scrape...")
    try:
        from scraper.api_client import scrape_latest_news
        from scraper.data_parser import parse_news_data
        from scraper.database import save_news_data
        
        # Get latest news
        news_data = scrape_latest_news()
        if news_data:
            # Parse the data
            parsed_data = parse_news_data(news_data)
            
            # Save to database
            save_news_data(parsed_data)
            
            print(f"✅ Initial scrape completed: {len(parsed_data)} items saved")
            return True
        else:
            print("⚠️  No data retrieved from API")
            return False
    except Exception as e:
        print(f"❌ Initial scrape failed: {e}")
        return False

def print_service_urls():
    """Print service URLs"""
    print("\n🌐 Service URLs:")
    print("=" * 50)
    
    # Get Railway project URL
    railway_url = os.getenv('RAILWAY_STATIC_URL')
    if railway_url:
        print(f"📊 Web Dashboard: https://{railway_url}")
    else:
        print("📊 Web Dashboard: https://your-project-name.up.railway.app")
    
    print("🔧 Scraper Service: Runs in background")
    print("🗄️  Database: PostgreSQL (managed by Railway)")
    
    print("\n📋 Next Steps:")
    print("=" * 50)
    print("1. Visit your web dashboard URL to see the analytics")
    print("2. Check the Railway dashboard for service logs")
    print("3. Monitor the scraping service in the background")
    print("4. Configure environment variables if needed")

def main():
    """Main setup function"""
    print("🚀 Gelonghui News Scraper - Railway Setup")
    print("=" * 50)
    
    # Check environment
    is_railway = check_environment()
    
    # Check database URL
    has_db_url = check_database_url()
    
    # Check requirements
    has_requirements = check_requirements()
    
    # Setup database if URL is available
    if has_db_url:
        db_setup = setup_database()
        db_test = test_database()
    else:
        db_setup = False
        db_test = False
    
    # Test API
    api_test = test_api()
    
    # Run initial scrape if database is working
    if db_test and api_test:
        initial_scrape = run_initial_scrape()
    else:
        initial_scrape = False
    
    # Print summary
    print("\n📊 Setup Summary:")
    print("=" * 50)
    print(f"Environment: {'✅ Railway' if is_railway else '⚠️  Local'}")
    print(f"Database URL: {'✅ Set' if has_db_url else '❌ Missing'}")
    print(f"Requirements: {'✅ Installed' if has_requirements else '❌ Missing'}")
    print(f"Database Setup: {'✅ Success' if db_setup else '❌ Failed'}")
    print(f"Database Test: {'✅ Success' if db_test else '❌ Failed'}")
    print(f"API Test: {'✅ Success' if api_test else '❌ Failed'}")
    print(f"Initial Scrape: {'✅ Success' if initial_scrape else '❌ Skipped'}")
    
    # Print service URLs
    print_service_urls()
    
    if has_db_url and db_test and api_test:
        print("\n🎉 Setup completed successfully!")
        print("Your Gelonghui News Scraper is ready to use!")
    else:
        print("\n⚠️  Setup completed with issues.")
        print("Please check the errors above and fix them.")

if __name__ == "__main__":
    main()