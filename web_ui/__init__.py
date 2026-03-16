"""
Web UI Package

Provides a Streamlit-based web interface for viewing and analyzing scraped news data.
"""

__version__ = "1.0.0"
__author__ = "Gelonghui Scraper Team"

from .app import create_app
from .dashboard import NewsDashboard
from .visualizations import ChartGenerator

__all__ = [
    'create_app',
    'NewsDashboard',
    'ChartGenerator'
]