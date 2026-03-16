import asyncio
import json
import re
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import jieba
from bs4 import BeautifulSoup
from loguru import logger

from .base_scraper import BaseScraper
from ..models.live_streams import LiveStream
from ..models.stream_content import StreamContent
from ..models.hashtags import Hashtag, TrendingTopic

class GelonghuiScraper(BaseScraper):
    """Scraper for 格隆汇 live streaming website"""
    
    def __init__(self, delay_range: tuple = (2, 5)):
        super().__init__("https://www.gelonghui.com", delay_range)
        self.api_base = "https://www.gelonghui.com/api"
        
    async def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        """Main scraping method for 格隆汇"""
        results = []
        
        # Scrape live streams
        live_streams = await self.scrape_live_streams()
        results.extend(live_streams)
        
        # Scrape stream content for active streams
        for stream in live_streams:
            if stream.get('status') == 'live':
                content = await self.scrape_stream_content(stream['stream_id'])
                results.extend(content)
                
        return results
        
    async def scrape_live_streams(self) -> List[Dict[str, Any]]:
        """Scrape live stream metadata"""
        logger.info("Scraping live streams from 格隆汇")
        
        # Try multiple approaches to get stream data
        streams = []
        
        # Method 1: Try to get data from API endpoints
        api_streams = await self.scrape_api_streams()
        streams.extend(api_streams)
        
        # Method 2: Scrape from main live page
        page_streams = await self.scrape_page_streams()
        streams.extend(page_streams)
        
        # Remove duplicates and validate
        unique_streams = self.deduplicate_streams(streams)
        
        logger.info(f"Found {len(unique_streams)} unique live streams")
        return unique_streams
        
    async def scrape_api_streams(self) -> List[Dict[str, Any]]:
        """Scrape stream data from API endpoints"""
        streams = []
        
        try:
            # Try common API endpoints
            api_endpoints = [
                f"{self.api_base}/live/list",
                f"{self.api_base}/live/streams",
                f"{self.api_base}/live/channels",
                f"{self.base_url}/api/live/list",
            ]
            
            for endpoint in api_endpoints:
                try:
                    content = await self.get_page_content(endpoint)
                    if content:
                        data = self.parse_api_response(content)
                        if data:
                            streams.extend(data)
                            logger.info(f"Found {len(data)} streams from {endpoint}")
                            break
                except Exception as e:
                    logger.debug(f"Failed to scrape {endpoint}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping API streams: {e}")
            
        return streams
        
    async def scrape_page_streams(self) -> List[Dict[str, Any]]:
        """Scrape stream data from the main live page"""
        streams = []
        
        try:
            # Get the main live page
            url = f"{self.base_url}/live?channelId=all"
            content = await self.get_dynamic_content(url, wait_selector="body")
            
            if not content:
                return streams
                
            soup = BeautifulSoup(content, 'html.parser')
            
            # Look for stream containers
            stream_containers = self.find_stream_containers(soup)
            
            for container in stream_containers:
                stream_data = self.extract_stream_data(container)
                if stream_data:
                    streams.append(stream_data)
                    
        except Exception as e:
            logger.error(f"Error scraping page streams: {e}")
            
        return streams
        
    def find_stream_containers(self, soup: BeautifulSoup) -> List[Any]:
        """Find stream containers in the page"""
        containers = []
        
        # Try different selectors for stream containers
        selectors = [
            '[class*="live"]',
            '[class*="stream"]',
            '[class*="channel"]',
            '.live-item',
            '.stream-item',
            '.channel-item',
            'div[data-stream-id]',
            'div[data-live-id]'
        ]
        
        for selector in selectors:
            try:
                found = soup.select(selector)
                if found:
                    containers.extend(found)
            except:
                continue
                
        return containers
        
    def extract_stream_data(self, container) -> Optional[Dict[str, Any]]:
        """Extract stream data from a container"""
        try:
            # Extract basic stream information
            stream_id = self.extract_stream_id(container)
            title = self.extract_title(container)
            viewer_count = self.extract_viewer_count(container)
            status = self.extract_status(container)
            thumbnail = self.extract_thumbnail(container)
            channel_info = self.extract_channel_info(container)
            
            if not stream_id or not title:
                return None
                
            return {
                'stream_id': stream_id,
                'title': title,
                'viewer_count': viewer_count,
                'status': status,
                'thumbnail_url': thumbnail,
                'channel_id': channel_info.get('id'),
                'channel_name': channel_info.get('name'),
                'platform_source': 'gelonghui',
                'scraped_at': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error extracting stream data: {e}")
            return None
            
    def extract_stream_id(self, container) -> Optional[str]:
        """Extract stream ID from container"""
        # Try different attributes and patterns
        id_attrs = ['data-stream-id', 'data-live-id', 'id', 'href']
        
        for attr in id_attrs:
            value = container.get(attr, '')
            if value:
                # Clean up the ID
                stream_id = re.sub(r'[^\w\-]', '', str(value))
                if stream_id and len(stream_id) > 3:
                    return stream_id
                    
        return None
        
    def extract_title(self, container) -> Optional[str]:
        """Extract stream title from container"""
        title_selectors = [
            '.title', '.stream-title', '.live-title', 'h3', 'h4',
            '[class*="title"]', '[class*="name"]'
        ]
        
        for selector in title_selectors:
            try:
                element = container.select_one(selector)
                if element:
                    title = element.get_text(strip=True)
                    if title and len(title) > 2:
                        return title
            except:
                continue
                
        return None
        
    def extract_viewer_count(self, container) -> Optional[int]:
        """Extract viewer count from container"""
        viewer_selectors = [
            '.viewer-count', '.viewers', '.audience', '.people',
            '[class*="viewer"]', '[class*="audience"]'
        ]
        
        for selector in viewer_selectors:
            try:
                element = container.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    # Extract number from text like "1.2万" or "12,345"
                    viewers = self.parse_viewer_count(text)
                    if viewers:
                        return viewers
            except:
                continue
                
        return 0
        
    def parse_viewer_count(self, text: str) -> Optional[int]:
        """Parse viewer count from text"""
        if not text:
            return 0
            
        # Remove common suffixes and clean text
        text = re.sub(r'[^\d.,万]', '', text)
        
        try:
            if '万' in text:
                # Handle Chinese "万" (10,000)
                number = float(text.replace('万', ''))
                return int(number * 10000)
            elif ',' in text:
                # Handle comma-separated numbers
                return int(text.replace(',', ''))
            else:
                return int(text)
        except:
            return 0
            
    def extract_status(self, container) -> str:
        """Extract stream status"""
        # Check for live indicators
        live_indicators = ['live', '直播中', '正在直播', 'on air']
        
        text = container.get_text().lower()
        for indicator in live_indicators:
            if indicator in text:
                return 'live'
                
        return 'scheduled'
        
    def extract_thumbnail(self, container) -> Optional[str]:
        """Extract thumbnail URL"""
        img_selectors = ['img', 'image', '[class*="thumb"]', '[class*="image"]']
        
        for selector in img_selectors:
            try:
                img = container.select_one(selector)
                if img:
                    src = img.get('src') or img.get('data-src') or img.get('srcset')
                    if src:
                        return self.normalize_url(src)
            except:
                continue
                
        return None
        
    def extract_channel_info(self, container) -> Dict[str, str]:
        """Extract channel information"""
        channel_info = {'id': None, 'name': None}
        
        # Try to find channel name
        channel_selectors = [
            '.channel-name', '.author', '.username', '.nickname',
            '[class*="channel"]', '[class*="author"]'
        ]
        
        for selector in channel_selectors:
            try:
                element = container.select_one(selector)
                if element:
                    name = element.get_text(strip=True)
                    if name:
                        channel_info['name'] = name
                        break
            except:
                continue
                
        return channel_info
        
    def normalize_url(self, url: str) -> str:
        """Normalize URL to absolute path"""
        if url.startswith('//'):
            return f"https:{url}"
        elif url.startswith('/'):
            return f"{self.base_url}{url}"
        return url
        
    def deduplicate_streams(self, streams: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate streams"""
        seen = set()
        unique_streams = []
        
        for stream in streams:
            stream_id = stream.get('stream_id')
            if stream_id and stream_id not in seen:
                seen.add(stream_id)
                unique_streams.append(stream)
                
        return unique_streams
        
    async def scrape_stream_content(self, stream_id: str) -> List[Dict[str, Any]]:
        """Scrape content from a specific stream"""
        content = []
        
        try:
            # Get stream page
            stream_url = f"{self.base_url}/live/{stream_id}"
            page_content = await self.get_dynamic_content(stream_url)
            
            if not page_content:
                return content
                
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Extract chat messages
            chat_messages = self.extract_chat_messages(soup, stream_id)
            content.extend(chat_messages)
            
            # Extract stream description
            description = self.extract_stream_description(soup, stream_id)
            if description:
                content.append(description)
                
        except Exception as e:
            logger.error(f"Error scraping stream content for {stream_id}: {e}")
            
        return content
        
    def extract_chat_messages(self, soup: BeautifulSoup, stream_id: str) -> List[Dict[str, Any]]:
        """Extract chat messages from stream page"""
        messages = []
        
        # Look for chat containers
        chat_selectors = [
            '.chat', '.message', '.comment', '.bubble',
            '[class*="chat"]', '[class*="message"]', '[class*="comment"]'
        ]
        
        for selector in chat_selectors:
            try:
                chat_elements = soup.select(selector)
                for element in chat_elements:
                    message = self.parse_chat_message(element, stream_id)
                    if message:
                        messages.append(message)
            except:
                continue
                
        return messages
        
    def parse_chat_message(self, element, stream_id: str) -> Optional[Dict[str, Any]]:
        """Parse a single chat message"""
        try:
            # Extract message text
            text_selectors = ['p', 'span', 'div', '.text', '.content']
            text = ""
            
            for selector in text_selectors:
                try:
                    text_element = element.select_one(selector)
                    if text_element:
                        text = text_element.get_text(strip=True)
                        if text:
                            break
                except:
                    continue
                    
            if not text:
                return None
                
            # Extract user info
            user_info = self.extract_message_user(element)
            
            # Extract timestamp
            timestamp = self.extract_message_timestamp(element)
            
            # Extract hashtags and mentions
            hashtags = self.extract_hashtags(text)
            mentions = self.extract_mentions(text)
            
            # Analyze sentiment
            sentiment = self.analyze_sentiment(text)
            
            return {
                'stream_id': stream_id,
                'timestamp': timestamp,
                'content_type': 'chat',
                'text_content': text,
                'hashtags': hashtags,
                'mentions': mentions,
                'sentiment_score': sentiment,
                'user_id': user_info.get('id'),
                'username': user_info.get('name'),
                'message_type': 'text',
                'scraped_at': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error parsing chat message: {e}")
            return None
            
    def extract_message_user(self, element) -> Dict[str, str]:
        """Extract user information from message"""
        user_info = {'id': None, 'name': None}
        
        # Look for user name
        user_selectors = [
            '.username', '.user', '.author', '.nickname',
            '[class*="user"]', '[class*="author"]'
        ]
        
        for selector in user_selectors:
            try:
                user_element = element.select_one(selector)
                if user_element:
                    name = user_element.get_text(strip=True)
                    if name:
                        user_info['name'] = name
                        break
            except:
                continue
                
        return user_info
        
    def extract_message_timestamp(self, element) -> Optional[datetime]:
        """Extract timestamp from message"""
        time_selectors = ['.time', '.timestamp', '.date', '[class*="time"]']
        
        for selector in time_selectors:
            try:
                time_element = element.select_one(selector)
                if time_element:
                    time_text = time_element.get_text(strip=True)
                    parsed_time = self.parse_timestamp(time_text)
                    if parsed_time:
                        return parsed_time
            except:
                continue
                
        return datetime.utcnow()
        
    def parse_timestamp(self, time_text: str) -> Optional[datetime]:
        """Parse timestamp from text"""
        if not time_text:
            return None
            
        # Common time formats
        time_patterns = [
            r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})\s*(\d{1,2}):(\d{2})',
            r'(\d{1,2})[-/](\d{1,2})\s*(\d{1,2}):(\d{2})',
            r'(\d{1,2}):(\d{2}):(\d{2})',
            r'(\d{1,2}):(\d{2})',
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, time_text)
            if match:
                try:
                    # This is a simplified parser - in production, use dateparser
                    now = datetime.now()
                    groups = match.groups()
                    
                    if len(groups) == 5:  # YYYY-MM-DD HH:MM
                        return datetime(int(groups[0]), int(groups[1]), int(groups[2]), 
                                       int(groups[3]), int(groups[4]))
                    elif len(groups) == 4:  # MM-DD HH:MM
                        return datetime(now.year, int(groups[0]), int(groups[1]), 
                                       int(groups[2]), int(groups[3]))
                    elif len(groups) == 3:  # HH:MM:SS
                        return datetime(now.year, now.month, now.day, 
                                       int(groups[0]), int(groups[1]), int(groups[2]))
                    elif len(groups) == 2:  # HH:MM
                        return datetime(now.year, now.month, now.day, 
                                       int(groups[0]), int(groups[1]))
                except:
                    continue
                    
        return None
        
    def extract_stream_description(self, soup: BeautifulSoup, stream_id: str) -> Optional[Dict[str, Any]]:
        """Extract stream description"""
        try:
            # Look for description elements
            desc_selectors = [
                '.description', '.desc', '.summary', '.intro',
                '[class*="description"]', '[class*="desc"]'
            ]
            
            for selector in desc_selectors:
                try:
                    desc_element = soup.select_one(selector)
                    if desc_element:
                        text = desc_element.get_text(strip=True)
                        if text:
                            hashtags = self.extract_hashtags(text)
                            mentions = self.extract_mentions(text)
                            sentiment = self.analyze_sentiment(text)
                            
                            return {
                                'stream_id': stream_id,
                                'timestamp': datetime.utcnow(),
                                'content_type': 'description',
                                'text_content': text,
                                'hashtags': hashtags,
                                'mentions': mentions,
                                'sentiment_score': sentiment,
                                'scraped_at': datetime.utcnow()
                            }
                except:
                    continue
                    
        except Exception as e:
            logger.error(f"Error extracting stream description: {e}")
            
        return None
        
    def extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        if not text:
            return []
            
        # Find hashtags (Chinese and English)
        hashtag_pattern = r'#([^#\s]+)#|#[^\s#]+'
        hashtags = re.findall(hashtag_pattern, text)
        
        # Clean and filter hashtags
        cleaned_hashtags = []
        for tag in hashtags:
            # Remove any trailing punctuation
            clean_tag = re.sub(r'[^\w\u4e00-\u9fff]', '', tag)
            if clean_tag and len(clean_tag) > 1:
                cleaned_hashtags.append(clean_tag)
                
        return cleaned_hashtags
        
    def extract_mentions(self, text: str) -> List[str]:
        """Extract user mentions from text"""
        if not text:
            return []
            
        # Find mentions (@username)
        mention_pattern = r'@([a-zA-Z0-9_\u4e00-\u9fff]+)'
        mentions = re.findall(mention_pattern, text)
        
        return mentions
        
    def analyze_sentiment(self, text: str) -> Optional[float]:
        """Simple sentiment analysis"""
        if not text:
            return None
            
        # This is a very basic implementation
        # In production, use a proper sentiment analysis library
        
        positive_words = ['好', '棒', '赞', '喜欢', '支持', '成功', '上涨', '利好']
        negative_words = ['差', '坏', '讨厌', '失望', '下跌', '利空', '问题', '风险']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count == 0 and negative_count == 0:
            return 0.0
            
        total = positive_count + negative_count
        score = (positive_count - negative_count) / total
        
        return round(score, 2)
        
    def parse_api_response(self, content: str) -> List[Dict[str, Any]]:
        """Parse API response content"""
        try:
            # Try to parse as JSON
            data = json.loads(content)
            
            # Handle different API response formats
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Look for data arrays in common keys
                for key in ['data', 'streams', 'live', 'result']:
                    if key in data and isinstance(data[key], list):
                        return data[key]
                        
        except json.JSONDecodeError:
            # Not JSON, try to extract JSON from HTML
            try:
                soup = BeautifulSoup(content, 'html.parser')
                scripts = soup.find_all('script')
                
                for script in scripts:
                    if script.string and 'json' in script.string.lower():
                        # Try to extract JSON from script
                        json_match = re.search(r'(\{.*\}|\[.*\])', script.string, re.DOTALL)
                        if json_match:
                            try:
                                data = json.loads(json_match.group(1))
                                if isinstance(data, list):
                                    return data
                            except:
                                continue
            except:
                pass
                
        return []