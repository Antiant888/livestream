"""
Data Parser Module

Handles parsing and extraction of news content, hashtags, and stock information
from Gelonghui API responses using regex patterns and data cleaning techniques.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class DataParser:
    """Parser for Gelonghui news data"""
    
    def __init__(self):
        # Regex patterns for hashtag extraction
        self.hashtag_patterns = [
            r'#([^#\s]+)#',  # Chinese hashtags: #话题#
            r'(?<!\w)#([A-Za-z0-9_]+)',  # English hashtags: #topic
            r'(?<!\w)＃([A-Za-z0-9_]+)＃',  # Chinese full-width hashtags
        ]
        
        # Regex patterns for stock symbol extraction
        self.stock_patterns = [
            r'([A-Z]{1,2})\s*(\d{4,6})\.(SH|SZ|HK)',  # Standard format: Market Code.Exchange
            r'(\d{4,6})\.(SH|SZ|HK)',  # Code.Exchange format
            r'([A-Z]{2,4})\s*(\d{4,6})',  # Market Code format
        ]
        
        # Content cleaning patterns
        self.content_cleaning_patterns = [
            (r'\s+', ' '),  # Normalize whitespace
            (r'\n+', '\n'),  # Normalize newlines
            (r'^\s+|\s+$', ''),  # Trim whitespace
        ]
    
    def extract_hashtags(self, text: str) -> List[str]:
        """
        Extract hashtags from text content
        
        Args:
            text: News content text
            
        Returns:
            List of extracted hashtags
        """
        if not text:
            return []
        
        hashtags = []
        
        for pattern in self.hashtag_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            hashtags.extend(matches)
        
        # Clean and normalize hashtags
        cleaned_hashtags = []
        for hashtag in hashtags:
            # Handle tuple matches (from groups)
            if isinstance(hashtag, tuple):
                hashtag = hashtag[0] if hashtag[0] else hashtag[1]
            
            # Clean hashtag text
            cleaned = self._clean_hashtag(hashtag)
            if cleaned and len(cleaned) > 1:  # Skip single character hashtags
                cleaned_hashtags.append(cleaned)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(cleaned_hashtags))
    
    def extract_stocks(self, related_stocks: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Extract stock information from API response
        
        Args:
            related_stocks: List of stock objects from API
            
        Returns:
            List of processed stock information
        """
        stocks = []
        
        if not related_stocks:
            return stocks
        
        for stock in related_stocks:
            try:
                stock_info = {
                    'market': stock.get('market', ''),
                    'code': stock.get('code', ''),
                    'name': stock.get('name', ''),
                    'can_click': stock.get('canClick', False),
                    'full_name': stock.get('fullName', ''),
                    'exchange': stock.get('exchange', ''),
                }
                
                # Validate stock information
                if self._is_valid_stock(stock_info):
                    stocks.append(stock_info)
                    
            except Exception as e:
                logger.warning(f"Error processing stock data: {e}")
                continue
        
        return stocks
    
    def extract_stocks_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract stock symbols from text content using regex
        
        Args:
            text: News content text
            
        Returns:
            List of extracted stock information
        """
        stocks = []
        
        for pattern in self.stock_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            
            for match in matches:
                try:
                    if len(match) == 3:  # (Market, Code, Exchange)
                        market, code, exchange = match
                    elif len(match) == 2:  # (Code, Exchange) or (Market, Code)
                        if '.' in match[1]:  # (Code, Exchange)
                            code, exchange = match
                            market = self._guess_market_from_exchange(exchange)
                        else:  # (Market, Code)
                            market, code = match
                            exchange = self._guess_exchange_from_market(market)
                    else:
                        continue
                    
                    stock_info = {
                        'market': market.upper(),
                        'code': code,
                        'name': '',  # Will be filled by API or left empty
                        'can_click': False,
                        'exchange': exchange.upper(),
                    }
                    
                    if self._is_valid_stock(stock_info):
                        stocks.append(stock_info)
                        
                except Exception as e:
                    logger.warning(f"Error extracting stock from text: {e}")
                    continue
        
        return stocks
    
    def parse_news_item(self, api_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse a single news item from API response
        
        Args:
            api_item: Raw news item from API
            
        Returns:
            Parsed and cleaned news item
        """
        try:
            # Extract basic fields
            parsed_item = {
                'glonghui_id': str(api_item.get('id', '')),
                'title': self._clean_text(api_item.get('title', '')),
                'content': self._clean_text(api_item.get('content', '')),
                'content_prefix': self._clean_text(api_item.get('contentPrefix', '')),
                'create_timestamp': api_item.get('createTimestamp', 0),
                'update_timestamp': api_item.get('updateTimestamp', 0),
                'level': api_item.get('level', 0),
                'route': api_item.get('route', ''),
                'close_comment': api_item.get('closeComment', False),
                
                # Engagement metrics
                'read_count': api_item.get('count', {}).get('read', 0),
                'comment_count': api_item.get('count', {}).get('comment', 0),
                'favorite_count': api_item.get('count', {}).get('favorite', 0),
                'like_count': api_item.get('count', {}).get('like', 0),
                'share_count': api_item.get('count', {}).get('share', 0),
                
                # Metadata
                'scraped_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            }
            
            # Convert timestamps to datetime objects
            if parsed_item['create_timestamp']:
                parsed_item['create_datetime'] = datetime.fromtimestamp(
                    parsed_item['create_timestamp']
                )
            else:
                parsed_item['create_datetime'] = None
            
            if parsed_item['update_timestamp']:
                parsed_item['update_datetime'] = datetime.fromtimestamp(
                    parsed_item['update_timestamp']
                )
            else:
                parsed_item['update_datetime'] = None
            
            # Calculate engagement score
            parsed_item['engagement_score'] = self._calculate_engagement_score(parsed_item)
            
            # Extract hashtags
            content_text = f"{parsed_item['title']} {parsed_item['content']}"
            parsed_item['hashtags'] = self.extract_hashtags(content_text)
            
            # Extract stocks from related data and content
            related_stocks = api_item.get('relatedStocks', [])
            content_stocks = self.extract_stocks_from_text(content_text)
            
            # Combine and deduplicate stocks
            all_stocks = self.extract_stocks(related_stocks) + content_stocks
            parsed_item['stocks'] = self._deduplicate_stocks(all_stocks)
            
            return parsed_item
            
        except Exception as e:
            logger.error(f"Error parsing news item: {e}")
            logger.error(f"Problematic item: {api_item}")
            return {}
    
    def _clean_hashtag(self, hashtag: str) -> str:
        """Clean and normalize hashtag text"""
        if not hashtag:
            return ''
        
        # Remove any remaining special characters
        cleaned = re.sub(r'[^\w\u4e00-\u9fff]', '', hashtag)
        
        # Remove leading/trailing whitespace
        cleaned = cleaned.strip()
        
        return cleaned
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ''
        
        # Apply cleaning patterns
        for pattern, replacement in self.content_cleaning_patterns:
            text = re.sub(pattern, replacement, text)
        
        return text.strip()
    
    def _is_valid_stock(self, stock_info: Dict[str, Any]) -> bool:
        """Validate stock information"""
        code = stock_info.get('code', '')
        market = stock_info.get('market', '')
        exchange = stock_info.get('exchange', '')
        
        # Basic validation
        if not code or not code.isdigit():
            return False
        
        if len(code) < 4 or len(code) > 6:
            return False
        
        # Validate market/exchange
        valid_markets = ['SH', 'SZ', 'HK', 'US', 'NASDAQ', 'NYSE']
        valid_exchanges = ['SH', 'SZ', 'HK', 'US', 'NASDAQ', 'NYSE']
        
        if market and market not in valid_markets:
            return False
        
        if exchange and exchange not in valid_exchanges:
            return False
        
        return True
    
    def _guess_market_from_exchange(self, exchange: str) -> str:
        """Guess market from exchange code"""
        exchange = exchange.upper()
        if exchange in ['SH', 'SHA']:
            return 'SH'
        elif exchange in ['SZ', 'SHE']:
            return 'SZ'
        elif exchange == 'HK':
            return 'HK'
        elif exchange in ['NASDAQ', 'NYSE', 'US']:
            return 'US'
        return ''
    
    def _guess_exchange_from_market(self, market: str) -> str:
        """Guess exchange from market code"""
        market = market.upper()
        if market in ['SH', 'SHA']:
            return 'SH'
        elif market in ['SZ', 'SHE']:
            return 'SZ'
        elif market == 'HK':
            return 'HK'
        elif market in ['US', 'NASDAQ', 'NYSE']:
            return 'US'
        return ''
    
    def _calculate_engagement_score(self, news_item: Dict[str, Any]) -> float:
        """
        Calculate engagement score based on read, share, and comment counts
        
        Formula: (reads * 0.1) + (shares * 2.0) + (comments * 1.0) + (likes * 0.5)
        """
        reads = news_item.get('read_count', 0)
        shares = news_item.get('share_count', 0)
        comments = news_item.get('comment_count', 0)
        likes = news_item.get('like_count', 0)
        
        score = (reads * 0.1) + (shares * 2.0) + (comments * 1.0) + (likes * 0.5)
        return round(score, 2)
    
    def _deduplicate_stocks(self, stocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate stocks based on market and code"""
        seen = set()
        unique_stocks = []
        
        for stock in stocks:
            key = (stock.get('market', ''), stock.get('code', ''))
            if key not in seen:
                seen.add(key)
                unique_stocks.append(stock)
        
        return unique_stocks


# Example usage and testing
if __name__ == "__main__":
    import logging
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test the data parser
    parser = DataParser()
    
    print("Testing Data Parser...")
    
    # Test hashtag extraction
    test_content = "这是一个测试内容 #测试话题# 和 #test_hashtag，还有 ＃另一个话题＃"
    hashtags = parser.extract_hashtags(test_content)
    print(f"Extracted hashtags: {hashtags}")
    
    # Test stock extraction
    test_stocks = [
        {'market': 'SH', 'code': '600000', 'name': '浦发银行', 'canClick': True}
    ]
    parsed_stocks = parser.extract_stocks(test_stocks)
    print(f"Extracted stocks: {parsed_stocks}")
    
    # Test stock extraction from text
    text_with_stocks = "今天关注浦发银行(600000.SH)和腾讯控股(0700.HK)的表现"
    text_stocks = parser.extract_stocks_from_text(text_with_stocks)
    print(f"Stocks from text: {text_stocks}")
    
    # Test news item parsing
    sample_item = {
        'id': 123456,
        'title': '测试新闻标题',
        'content': '这是一个测试新闻内容 #测试话题# 关注600000.SH',
        'contentPrefix': '格隆汇测试｜',
        'createTimestamp': 1647244800,
        'updateTimestamp': 1647244800,
        'level': 1,
        'route': 'https://www.gelonghui.com/test/123456',
        'closeComment': False,
        'count': {
            'read': 100,
            'comment': 10,
            'favorite': 5,
            'like': 20,
            'share': 3
        },
        'relatedStocks': [
            {'market': 'SH', 'code': '600000', 'name': '浦发银行', 'canClick': True}
        ]
    }
    
    parsed_item = parser.parse_news_item(sample_item)
    print(f"Parsed news item: {json.dumps(parsed_item, indent=2, ensure_ascii=False)}")