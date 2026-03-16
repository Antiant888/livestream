"""
Scraper Scheduler

Handles periodic scraping of Gelonghui API with incremental timestamps,
managing the scraping workflow and monitoring.
"""

import logging
import time
import os
import signal
import sys
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from datetime import datetime, timedelta

from .api_client import GelonghuiAPIClient
from .data_parser import DataParser
from .database import DatabaseManager

logger = logging.getLogger(__name__)


class ScraperScheduler:
    """Scheduler for periodic news scraping"""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize the scraper scheduler
        
        Args:
            database_url: Database connection URL (optional, uses env var if not provided)
        """
        self.database_url = database_url or os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("Database URL must be provided via parameter or DATABASE_URL environment variable")
        
        self.scheduler = BackgroundScheduler()
        self.last_timestamp = 0
        self.is_running = False
        self.db_manager = None
        self.api_client = None
        self.parser = None
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Set up scheduler event listeners
        self.scheduler.add_listener(self._job_executed, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self._job_error, EVENT_JOB_ERROR)
        
        logger.info("Scraper scheduler initialized")
    
    def start(self, interval_minutes: Optional[int] = None):
        """
        Start the scraping scheduler
        
        Args:
            interval_minutes: Scraping interval in minutes (optional, uses env var if not provided)
        """
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        # Initialize components
        self._initialize_components()
        
        # Get scraping interval
        interval = interval_minutes or int(os.getenv('SCRAPING_INTERVAL_MINUTES', 1))
        
        # Add scraping job
        self.scheduler.add_job(
            func=self._scrape_job,
            trigger=IntervalTrigger(minutes=interval),
            id='news_scraper',
            name='Gelonghui News Scraper',
            replace_existing=True,
            max_instances=1,  # Prevent overlapping jobs
            coalesce=True     # Run missed jobs immediately
        )
        
        # Start scheduler
        self.scheduler.start()
        self.is_running = True
        
        logger.info(f"Scraper scheduler started with {interval}-minute intervals")
        logger.info(f"Initial timestamp: {self.last_timestamp}")
        
        # Keep the main thread alive
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
            self.stop()
    
    def stop(self):
        """Stop the scraping scheduler"""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
        
        self.is_running = False
        self.scheduler.shutdown(wait=True)
        
        if self.db_manager:
            self.db_manager.close()
        
        logger.info("Scraper scheduler stopped")
    
    def _initialize_components(self):
        """Initialize scraper components"""
        try:
            # Initialize database manager
            self.db_manager = DatabaseManager(self.database_url)
            
            # Get last timestamp from database
            self.last_timestamp = self.db_manager.get_latest_timestamp()
            logger.info(f"Retrieved last timestamp from database: {self.last_timestamp}")
            
            # Initialize API client
            self.api_client = GelonghuiAPIClient()
            
            # Initialize data parser
            self.parser = DataParser()
            
            logger.info("Scraper components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize scraper components: {e}")
            raise
    
    def _scrape_job(self):
        """Main scraping job executed by the scheduler"""
        job_start_time = datetime.utcnow()
        logger.info(f"Starting scraping job at {job_start_time}")
        
        try:
            # Fetch new news items
            data = self.api_client.get_live_news(
                category='all',
                limit=15,
                timestamp=self.last_timestamp
            )
            
            if not data or 'result' not in data:
                logger.warning("No data received from API")
                return
            
            new_items = data['result']
            logger.info(f"Received {len(new_items)} new items from API")
            
            processed_count = 0
            for item in new_items:
                try:
                    # Parse the news item
                    parsed_data = self.parser.parse_news_item(item)
                    
                    if not parsed_data:
                        logger.warning(f"Failed to parse news item: {item.get('id')}")
                        continue
                    
                    # Insert into database
                    success = self.db_manager.insert_news_item(parsed_data)
                    
                    if success:
                        # Insert related data
                        news_item_id = parsed_data['glonghui_id']
                        
                        # Insert hashtags
                        if 'hashtags' in parsed_data:
                            self.db_manager.insert_hashtags(news_item_id, parsed_data['hashtags'])
                        
                        # Insert stocks
                        if 'stocks' in parsed_data:
                            self.db_manager.insert_stocks(news_item_id, parsed_data['stocks'])
                        
                        # Update timestamp
                        item_timestamp = item.get('createTimestamp', 0)
                        if item_timestamp > self.last_timestamp:
                            self.last_timestamp = item_timestamp
                        
                        processed_count += 1
                    else:
                        logger.error(f"Failed to insert news item: {parsed_data.get('glonghui_id')}")
                        
                except Exception as e:
                    logger.error(f"Error processing news item: {e}")
                    continue
            
            job_end_time = datetime.utcnow()
            job_duration = (job_end_time - job_start_time).total_seconds()
            
            logger.info(
                f"Scraping job completed: "
                f"processed={processed_count}, "
                f"duration={job_duration:.2f}s, "
                f"new_timestamp={self.last_timestamp}"
            )
            
        except Exception as e:
            logger.error(f"Scraping job failed: {e}")
            raise
    
    def _job_executed(self, event):
        """Handle successful job execution"""
        logger.info(f"Job {event.job_id} executed successfully")
    
    def _job_error(self, event):
        """Handle job execution errors"""
        logger.error(f"Job {event.job_id} failed: {event.exception}")
        
        # Log additional error details
        if hasattr(event, 'traceback'):
            logger.error(f"Traceback: {event.traceback}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.stop()
        sys.exit(0)
    
    def get_status(self) -> dict:
        """Get current scheduler status"""
        return {
            'is_running': self.is_running,
            'last_timestamp': self.last_timestamp,
            'job_count': len(self.scheduler.get_jobs()),
            'next_run_time': str(self.scheduler.get_job('news_scraper').next_run_time) if self.scheduler.get_job('news_scraper') else None
        }
    
    def test_connection(self) -> bool:
        """Test API and database connections"""
        try:
            # Test API connection
            if not self.api_client.test_connection():
                logger.error("API connection test failed")
                return False
            
            # Test database connection
            test_count = self.db_manager.get_news_count('1h')
            logger.info(f"Database test successful, found {test_count} recent news items")
            
            return True
            
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


# Example usage and testing
if __name__ == "__main__":
    import logging
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test the scheduler
    print("Testing Scraper Scheduler...")
    
    # Use SQLite for testing
    scheduler = ScraperScheduler("sqlite:///test_scheduler.db")
    
    # Test connections
    if scheduler.test_connection():
        print("✅ All connections successful")
        
        # Start scheduler for testing (1-minute intervals)
        print("Starting scheduler for 5 minutes (test mode)...")
        try:
            # Run for a short time for testing
            import threading
            import time
            
            def stop_scheduler():
                time.sleep(300)  # Run for 5 minutes
                scheduler.stop()
                print("Scheduler stopped after test period")
            
            stop_thread = threading.Thread(target=stop_scheduler)
            stop_thread.daemon = True
            stop_thread.start()
            
            scheduler.start(interval_minutes=1)
            
        except KeyboardInterrupt:
            print("Test interrupted by user")
    else:
        print("❌ Connection test failed")
    
    print("Scheduler test completed")