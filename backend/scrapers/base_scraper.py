import asyncio
import logging
import random
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import httpx
from playwright.async_api import async_playwright
from loguru import logger

class BaseScraper(ABC):
    """Base scraper class with common functionality"""
    
    def __init__(self, base_url: str, delay_range: tuple = (1, 3)):
        self.base_url = base_url
        self.delay_range = delay_range
        self.session = None
        self.browser = None
        self.page = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()
        
    async def initialize(self):
        """Initialize scraper resources"""
        # Create HTTP session
        self.session = httpx.AsyncClient(
            headers=self.get_headers(),
            timeout=30.0,
            follow_redirects=True
        )
        
        # Initialize browser for dynamic content
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()
        
    async def cleanup(self):
        """Clean up scraper resources"""
        if self.session:
            await self.session.aclose()
        if self.browser:
            await self.browser.close()
            
    def get_headers(self) -> Dict[str, str]:
        """Get realistic browser headers"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        ]
        
        return {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
    async def random_delay(self):
        """Add random delay to avoid rate limiting"""
        delay = random.uniform(*self.delay_range)
        await asyncio.sleep(delay)
        
    async def get_page_content(self, url: str) -> Optional[str]:
        """Get page content using HTTP client"""
        try:
            await self.random_delay()
            response = await self.session.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
            
    async def get_dynamic_content(self, url: str, wait_selector: str = None) -> Optional[str]:
        """Get dynamic content using browser automation"""
        try:
            await self.random_delay()
            await self.page.goto(url, wait_until='networkidle')
            
            if wait_selector:
                await self.page.wait_for_selector(wait_selector, timeout=10000)
                
            return await self.page.content()
        except Exception as e:
            logger.error(f"Error fetching dynamic content from {url}: {e}")
            return None
            
    @abstractmethod
    async def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        """Main scraping method to be implemented by subclasses"""
        pass