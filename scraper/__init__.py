"""
Gelonghui News Scraper - Main Package

This package provides a comprehensive solution for scraping real-time news data
from the Gelonghui API, parsing the content, and storing it in a PostgreSQL database.

Key Components:
- API Client: Handles HTTP requests to Gelonghui API
- Data Parser: Extracts and processes news content, hashtags, and stocks
- Database Manager: Manages PostgreSQL operations
- Scheduler: Handles periodic scraping with incremental timestamps
"""

__version__ = "1.0.0"
__author__ = "Gelonghui Scraper Team"
__email__ = "scraper@example.com"

from .api_client import GelonghuiAPIClient
from .data_parser import DataParser
from .database import DatabaseManager
from .scheduler import ScraperScheduler

__all__ = [
    'GelonghuiAPIClient',
    'DataParser', 
    'DatabaseManager',
    'ScraperScheduler'
]