"""
Database Manager

Handles database operations including connection management, CRUD operations,
and data integrity for the Gelonghui news scraper.
"""

import logging
from typing import List, Dict, Any, Optional, Union
from sqlalchemy import create_engine, text, func, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import datetime, timedelta
from .models import Base, NewsItem, Stock, Hashtag, Trend
from .data_parser import DataParser

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database manager for Gelonghui news scraper"""
    
    def __init__(self, database_url: str):
        """
        Initialize database manager
        
        Args:
            database_url: Database connection URL
        """
        self.engine = create_engine(
            database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        self.Session = sessionmaker(bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(self.engine)
        
        # Initialize data parser for hashtag extraction
        self.parser = DataParser()
        
        logger.info("Database manager initialized")
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.Session()
    
    def insert_news_item(self, news_data: Dict[str, Any]) -> bool:
        """
        Insert or update a news item
        
        Args:
            news_data: Parsed news item data
            
        Returns:
            True if successful, False otherwise
        """
        session = self.get_session()
        
        try:
            # Check if item already exists
            existing = session.query(NewsItem).filter_by(
                glonghui_id=news_data['glonghui_id']
            ).first()
            
            if existing:
                # Update existing item
                for key, value in news_data.items():
                    if key not in ['id', 'created_at', 'stocks', 'hashtags']:
                        setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
                
                # Update engagement score
                existing.calculate_engagement_score()
                
                logger.info(f"Updated existing news item: {news_data['glonghui_id']}")
            else:
                # Create new item
                news_item = NewsItem(**news_data)
                session.add(news_item)
                
                logger.info(f"Inserted new news item: {news_data['glonghui_id']}")
            
            session.commit()
            return True
            
        except IntegrityError as e:
            session.rollback()
            logger.warning(f"Duplicate news item: {news_data.get('glonghui_id')}")
            return True  # Consider duplicate as success
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error inserting news item: {e}")
            return False
        finally:
            session.close()
    
    def insert_hashtags(self, news_item_id: int, hashtags: List[str]) -> bool:
        """
        Insert hashtags for a news item
        
        Args:
            news_item_id: ID of the news item
            hashtags: List of hashtags
            
        Returns:
            True if successful, False otherwise
        """
        session = self.get_session()
        
        try:
            # Remove existing hashtags for this news item
            session.query(Hashtag).filter_by(news_item_id=news_item_id).delete()
            
            # Insert new hashtags
            for hashtag_text in hashtags:
                hashtag = Hashtag(
                    news_item_id=news_item_id,
                    hashtag_text=hashtag_text,
                    frequency=1
                )
                session.add(hashtag)
            
            session.commit()
            logger.info(f"Inserted {len(hashtags)} hashtags for news item {news_item_id}")
            return True
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error inserting hashtags: {e}")
            return False
        finally:
            session.close()
    
    def insert_stocks(self, news_item_id: int, stocks: List[Dict[str, Any]]) -> bool:
        """
        Insert stocks for a news item
        
        Args:
            news_item_id: ID of the news item
            stocks: List of stock dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        session = self.get_session()
        
        try:
            # Remove existing stocks for this news item
            session.query(Stock).filter_by(news_item_id=news_item_id).delete()
            
            # Insert new stocks
            for stock_data in stocks:
                stock = Stock(
                    news_item_id=news_item_id,
                    market=stock_data.get('market', ''),
                    code=stock_data.get('code', ''),
                    name=stock_data.get('name', ''),
                    can_click=stock_data.get('can_click', False),
                    full_name=stock_data.get('full_name', ''),
                    exchange=stock_data.get('exchange', '')
                )
                session.add(stock)
            
            session.commit()
            logger.info(f"Inserted {len(stocks)} stocks for news item {news_item_id}")
            return True
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error inserting stocks: {e}")
            return False
        finally:
            session.close()
    
    def get_latest_timestamp(self) -> int:
        """
        Get the latest timestamp from stored news items
        
        Returns:
            Latest timestamp or 0 if no items exist
        """
        session = self.get_session()
        
        try:
            latest = session.query(func.max(NewsItem.create_timestamp)).scalar()
            return latest or 0
        except SQLAlchemyError as e:
            logger.error(f"Error getting latest timestamp: {e}")
            return 0
        finally:
            session.close()
    
    def get_news_count(self, time_range: str = '24h') -> int:
        """
        Get news count for a time range
        
        Args:
            time_range: Time range ('1h', '24h', '7d')
            
        Returns:
            Count of news items
        """
        session = self.get_session()
        
        try:
            cutoff_time = self._get_cutoff_time(time_range)
            count = session.query(NewsItem).filter(
                NewsItem.create_timestamp >= cutoff_time
            ).count()
            return count
        except SQLAlchemyError as e:
            logger.error(f"Error getting news count: {e}")
            return 0
        finally:
            session.close()
    
    def get_top_hashtags(self, time_range: str = '24h', limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top hashtags by frequency
        
        Args:
            time_range: Time range ('1h', '24h', '7d')
            limit: Number of hashtags to return
            
        Returns:
            List of hashtag dictionaries with frequency
        """
        session = self.get_session()
        
        try:
            cutoff_time = self._get_cutoff_time(time_range)
            
            # Query to get hashtag frequencies
            results = session.query(
                Hashtag.hashtag_text,
                func.count(Hashtag.id).label('frequency')
            ).join(NewsItem).filter(
                NewsItem.create_timestamp >= cutoff_time
            ).group_by(Hashtag.hashtag_text).order_by(
                func.count(Hashtag.id).desc()
            ).limit(limit).all()
            
            return [
                {'hashtag': row.hashtag_text, 'frequency': row.frequency}
                for row in results
            ]
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting top hashtags: {e}")
            return []
        finally:
            session.close()
    
    def get_top_engaged_items(self, time_range: str = '24h', limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top engaged news items
        
        Args:
            time_range: Time range ('1h', '24h', '7d')
            limit: Number of items to return
            
        Returns:
            List of news item dictionaries
        """
        session = self.get_session()
        
        try:
            cutoff_time = self._get_cutoff_time(time_range)
            
            # Query to get top engaged items
            results = session.query(NewsItem).filter(
                NewsItem.create_timestamp >= cutoff_time
            ).order_by(
                NewsItem.engagement_score.desc()
            ).limit(limit).all()
            
            return [item.to_dict() for item in results]
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting top engaged items: {e}")
            return []
        finally:
            session.close()
    
    def get_hashtag_trends(self, hashtag: str, time_range: str = '24h') -> List[Dict[str, Any]]:
        """
        Get hashtag trends over time
        
        Args:
            hashtag: Hashtag to analyze
            time_range: Time range ('1h', '24h', '7d')
            
        Returns:
            List of trend data points
        """
        session = self.get_session()
        
        try:
            cutoff_time = self._get_cutoff_time(time_range)
            
            # Query to get hashtag frequency over time
            results = session.query(
                func.date_trunc('hour', NewsItem.created_at).label('time_bucket'),
                func.count(Hashtag.id).label('frequency')
            ).join(Hashtag).filter(
                and_(
                    Hashtag.hashtag_text == hashtag,
                    NewsItem.create_timestamp >= cutoff_time
                )
            ).group_by(
                func.date_trunc('hour', NewsItem.created_at)
            ).order_by(
                'time_bucket'
            ).all()
            
            return [
                {
                    'timestamp': row.time_bucket.isoformat(),
                    'frequency': row.frequency
                }
                for row in results
            ]
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting hashtag trends: {e}")
            return []
        finally:
            session.close()
    
    def get_stock_mentions(self, time_range: str = '24h', limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most mentioned stocks
        
        Args:
            time_range: Time range ('1h', '24h', '7d')
            limit: Number of stocks to return
            
        Returns:
            List of stock dictionaries with mention count
        """
        session = self.get_session()
        
        try:
            cutoff_time = self._get_cutoff_time(time_range)
            
            # Query to get stock mentions
            results = session.query(
                Stock.code,
                Stock.name,
                Stock.market,
                func.count(Stock.id).label('mentions')
            ).join(NewsItem).filter(
                NewsItem.create_timestamp >= cutoff_time
            ).group_by(
                Stock.code, Stock.name, Stock.market
            ).order_by(
                func.count(Stock.id).desc()
            ).limit(limit).all()
            
            return [
                {
                    'code': row.code,
                    'name': row.name,
                    'market': row.market,
                    'mentions': row.mentions
                }
                for row in results
            ]
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting stock mentions: {e}")
            return []
        finally:
            session.close()
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> bool:
        """
        Clean up old data beyond retention period
        
        Args:
            days_to_keep: Number of days to keep data
            
        Returns:
            True if successful, False otherwise
        """
        session = self.get_session()
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Delete old trends
            deleted_trends = session.query(Trend).filter(
                Trend.timestamp < cutoff_date
            ).delete()
            
            # Delete old news items (this will cascade to related stocks and hashtags)
            deleted_news = session.query(NewsItem).filter(
                NewsItem.created_at < cutoff_date
            ).delete()
            
            session.commit()
            
            logger.info(f"Cleaned up {deleted_news} old news items and {deleted_trends} old trends")
            return True
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error cleaning up old data: {e}")
            return False
        finally:
            session.close()
    
    def _get_cutoff_time(self, time_range: str) -> int:
        """
        Get cutoff timestamp for time range
        
        Args:
            time_range: Time range ('1h', '24h', '7d')
            
        Returns:
            Unix timestamp
        """
        now = datetime.utcnow()
        
        if time_range == '1h':
            cutoff = now - timedelta(hours=1)
        elif time_range == '24h':
            cutoff = now - timedelta(hours=24)
        elif time_range == '7d':
            cutoff = now - timedelta(days=7)
        else:
            cutoff = now - timedelta(hours=24)  # Default to 24h
        
        return int(cutoff.timestamp())
    
    def close(self):
        """Close database connection"""
        self.engine.dispose()
        logger.info("Database connection closed")


# Example usage and testing
if __name__ == "__main__":
    import logging
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test database manager
    print("Testing Database Manager...")
    
    # Use SQLite for testing
    db_manager = DatabaseManager("sqlite:///test_news.db")
    
    # Test inserting a news item
    test_news = {
        'glonghui_id': 'test_123',
        'title': 'Test News Title',
        'content': 'This is test content with #test_hashtag',
        'content_prefix': 'Test Prefix｜',
        'create_timestamp': int(datetime.utcnow().timestamp()),
        'update_timestamp': int(datetime.utcnow().timestamp()),
        'level': 1,
        'route': 'https://test.com/news/123',
        'close_comment': False,
        'read_count': 100,
        'comment_count': 10,
        'favorite_count': 5,
        'like_count': 20,
        'share_count': 3,
        'scraped_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
    }
    
    success = db_manager.insert_news_item(test_news)
    print(f"News insertion success: {success}")
    
    # Test getting latest timestamp
    latest_ts = db_manager.get_latest_timestamp()
    print(f"Latest timestamp: {latest_ts}")
    
    # Test cleanup
    db_manager.cleanup_old_data(days_to_keep=1)
    
    # Close connection
    db_manager.close()
    
    print("Database manager test completed")