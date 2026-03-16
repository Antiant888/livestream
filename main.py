"""
Main Entry Point

Provides command-line interface for the Gelonghui news scraper application.
"""

import argparse
import logging
import os
import sys
import time
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.scheduler import ScraperScheduler
from scraper.api_client import GelonghuiAPIClient
from scraper.database import DatabaseManager
from web_ui.app import NewsDashboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def test_api():
    """Test API connection"""
    logger.info("Testing API connection...")
    
    client = GelonghuiAPIClient()
    if client.test_connection():
        logger.info("✅ API connection successful")
        return True
    else:
        logger.error("❌ API connection failed")
        return False


def test_database(database_url):
    """Test database connection"""
    logger.info("Testing database connection...")
    
    try:
        db_manager = DatabaseManager(database_url)
        count = db_manager.get_news_count('1h')
        logger.info(f"✅ Database connection successful, found {count} recent items")
        db_manager.close()
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


def run_scraper(database_url, interval_minutes):
    """Run the scraper in daemon mode"""
    logger.info(f"Starting scraper with {interval_minutes}-minute intervals")
    logger.info(f"Database URL: {database_url}")
    
    try:
        scheduler = ScraperScheduler(database_url)
        
        # Test connections before starting
        if not scheduler.test_connection():
            logger.error("Connection tests failed, exiting")
            return False
        
        logger.info("Starting scraper scheduler...")
        scheduler.start(interval_minutes=interval_minutes)
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Scraper failed: {e}")
        return False
    
    return True


def run_dashboard(database_url):
    """Run the web dashboard"""
    logger.info("Starting web dashboard...")
    
    # Set environment variable for database URL
    os.environ['DATABASE_URL'] = database_url
    
    try:
        # Import and run Streamlit app
        import streamlit.web.bootstrap as bootstrap
        import streamlit.web.cli as cli
        
        # Run the dashboard
        dashboard = NewsDashboard()
        dashboard.run()
        
    except Exception as e:
        logger.error(f"Dashboard failed: {e}")
        return False
    
    return True


def setup_database(database_url):
    """Initialize database schema"""
    logger.info("Setting up database schema...")
    
    try:
        db_manager = DatabaseManager(database_url)
        logger.info("✅ Database schema created successfully")
        db_manager.close()
        return True
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        return False


def show_status(database_url):
    """Show current system status"""
    logger.info("Showing system status...")
    
    try:
        db_manager = DatabaseManager(database_url)
        
        # Get statistics
        total_news = db_manager.get_news_count('24h')
        latest_timestamp = db_manager.get_latest_timestamp()
        
        if latest_timestamp:
            last_update = datetime.fromtimestamp(latest_timestamp)
        else:
            last_update = "No data"
        
        top_hashtags = db_manager.get_top_hashtags('24h', 3)
        top_stocks = db_manager.get_stock_mentions('24h', 3)
        
        print("\n" + "="*50)
        print("📊 GELONGHUI NEWS SCRAPER STATUS")
        print("="*50)
        print(f"Total News (24h): {total_news}")
        print(f"Last Update: {last_update}")
        print(f"Top Hashtags: {[h['hashtag'] for h in top_hashtags]}")
        print(f"Top Stocks: {[s['code'] for s in top_stocks]}")
        print("="*50)
        
        db_manager.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Status check failed: {e}")
        return False


def cleanup_data(database_url, days_to_keep):
    """Clean up old data"""
    logger.info(f"Cleaning up data older than {days_to_keep} days...")
    
    try:
        db_manager = DatabaseManager(database_url)
        success = db_manager.cleanup_old_data(days_to_keep)
        db_manager.close()
        
        if success:
            logger.info("✅ Data cleanup completed successfully")
        else:
            logger.error("❌ Data cleanup failed")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Data cleanup failed: {e}")
        return False


def main():
    """Main command-line interface"""
    parser = argparse.ArgumentParser(
        description="Gelonghui News Scraper - Real-time news scraping and analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py test --api                    # Test API connection
  python main.py test --database               # Test database connection
  python main.py setup                         # Set up database schema
  python main.py run --scraper                 # Run scraper daemon
  python main.py run --dashboard               # Run web dashboard
  python main.py status                        # Show system status
  python main.py cleanup --days 30             # Clean up old data
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test connections')
    test_parser.add_argument('--api', action='store_true', help='Test API connection')
    test_parser.add_argument('--database', action='store_true', help='Test database connection')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Set up database schema')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run scraper or dashboard')
    run_parser.add_argument('--scraper', action='store_true', help='Run scraper daemon')
    run_parser.add_argument('--dashboard', action='store_true', help='Run web dashboard')
    run_parser.add_argument('--interval', type=int, default=1, help='Scraping interval in minutes (default: 1)')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old data')
    cleanup_parser.add_argument('--days', type=int, default=30, help='Keep data for N days (default: 30)')
    
    # Global arguments
    parser.add_argument('--database-url', default=os.getenv('DATABASE_URL', 'sqlite:///news_data.db'),
                       help='Database connection URL (default: sqlite:///news_data.db)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Handle commands
    if args.command == 'test':
        success = True
        if args.api:
            success &= test_api()
        if args.database:
            success &= test_database(args.database_url)
        
        if not args.api and not args.database:
            # Test both if no specific test requested
            success &= test_api()
            success &= test_database(args.database_url)
        
        sys.exit(0 if success else 1)
    
    elif args.command == 'setup':
        success = setup_database(args.database_url)
        sys.exit(0 if success else 1)
    
    elif args.command == 'run':
        if args.scraper:
            success = run_scraper(args.database_url, args.interval)
            sys.exit(0 if success else 1)
        elif args.dashboard:
            success = run_dashboard(args.database_url)
            sys.exit(0 if success else 1)
        else:
            print("Error: Please specify --scraper or --dashboard")
            sys.exit(1)
    
    elif args.command == 'status':
        success = show_status(args.database_url)
        sys.exit(0 if success else 1)
    
    elif args.command == 'cleanup':
        success = cleanup_data(args.database_url, args.days)
        sys.exit(0 if success else 1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()