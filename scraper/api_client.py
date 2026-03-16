"""
Gelonghui API Client

Handles HTTP requests to the Gelonghui live news API with proper error handling,
rate limiting, and retry mechanisms.
"""

import requests
import time
import logging
from typing import Optional, Dict, Any, Union
from urllib.parse import urljoin
import random

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter to respect API limits"""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.interval = 60.0 / requests_per_minute
        self.last_request_time = 0
    
    def wait_if_needed(self):
        """Wait if we need to respect rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.interval:
            sleep_time = self.interval - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()


class GelonghuiAPIClient:
    """Client for interacting with Gelonghui live news API"""
    
    def __init__(self, base_url: str = "https://www.gelonghui.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.rate_limiter = RateLimiter(requests_per_minute=60)
        
        # Set up headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.gelonghui.com/',
            'Origin': 'https://www.gelonghui.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Connection': 'keep-alive'
        })
    
    def _get_random_user_agent(self) -> str:
        """Get a random user agent to avoid detection"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]
        return random.choice(user_agents)
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Make HTTP request with retry logic"""
        url = urljoin(self.base_url, endpoint)
        
        # Respect rate limits
        self.rate_limiter.wait_if_needed()
        
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Making request to {url} with params: {params}")
                
                response = self.session.get(
                    url,
                    params=params,
                    timeout=15,
                    allow_redirects=True
                )
                
                # Check for successful response
                response.raise_for_status()
                
                # Parse JSON response
                data = response.json()
                
                # Check API-specific error codes
                if isinstance(data, dict) and data.get('statusCode') != 200:
                    logger.warning(f"API returned non-200 status: {data.get('statusCode')}")
                    return None
                
                logger.info(f"Successfully fetched data from {url}")
                return data
                
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{max_retries})")
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error (attempt {attempt + 1}/{max_retries})")
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code
                if status_code == 429:
                    logger.error("Rate limited by server")
                    return None
                elif status_code in [500, 502, 503, 504]:
                    logger.warning(f"Server error {status_code}, retrying...")
                else:
                    logger.error(f"HTTP error {status_code}: {e}")
                    return None
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
            except ValueError as e:
                logger.error(f"JSON decode error: {e}")
            
            # Wait before retrying (exponential backoff)
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
        
        logger.error(f"Failed to fetch data after {max_retries} attempts")
        return None
    
    def get_live_news(self, 
                     category: str = "all", 
                     limit: int = 15, 
                     timestamp: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch live news from Gelonghui API
        
        Args:
            category: News category (default: "all")
            limit: Number of items to fetch (default: 15)
            timestamp: Unix timestamp for incremental updates (optional)
        
        Returns:
            Parsed JSON response or None if failed
        """
        endpoint = "/api/live-channels/all/lives/v4"
        params = {
            'category': category,
            'limit': limit
        }
        
        if timestamp:
            params['timestamp'] = timestamp
        
        return self._make_request(endpoint, params)
    
    def get_news_by_id(self, news_id: Union[str, int]) -> Optional[Dict[str, Any]]:
        """
        Fetch specific news item by ID
        
        Args:
            news_id: News item ID
        
        Returns:
            Parsed JSON response or None if failed
        """
        endpoint = f"/api/live-channels/all/lives/v4/{news_id}"
        return self._make_request(endpoint)
    
    def test_connection(self) -> bool:
        """
        Test API connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            data = self.get_live_news(limit=1)
            if data and 'result' in data:
                logger.info("API connection test successful")
                return True
            else:
                logger.warning("API connection test failed - no data returned")
                return False
        except Exception as e:
            logger.error(f"API connection test failed: {e}")
            return False


# Example usage and testing
if __name__ == "__main__":
    import logging
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test the API client
    client = GelonghuiAPIClient()
    
    print("Testing Gelonghui API Client...")
    
    # Test connection
    if client.test_connection():
        print("✅ API connection successful")
        
        # Test fetching news
        data = client.get_live_news(limit=5)
        if data:
            print(f"✅ Successfully fetched {len(data.get('result', []))} news items")
            
            # Print first item details
            if data.get('result'):
                first_item = data['result'][0]
                print(f"First item ID: {first_item.get('id')}")
                print(f"First item title: {first_item.get('title', 'No title')}")
                print(f"Content preview: {first_item.get('content', '')[:100]}...")
        else:
            print("❌ Failed to fetch news data")
    else:
        print("❌ API connection failed")