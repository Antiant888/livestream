# Technical Implementation Guide for 格隆汇 Live Streaming Analysis

## Overview

Based on the comprehensive website analysis, this guide provides specific technical recommendations for implementing a robust data extraction and monitoring system for the 格隆汇 live streaming platform.

## Architecture Design

### System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Browser       │    │   Scraping       │    │   Data          │
│   Automation    │───▶│   Engine         │───▶│   Processing    │
│   (Playwright)  │    │   (Python)       │    │   (Analysis)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Network       │    │   Anti-Scraping  │    │   Database      │
│   Monitoring    │    │   Bypass         │    │   (PostgreSQL)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Implementation Phases

### Phase 1: Dynamic Content Analysis Setup

#### 1.1 Browser Automation Configuration

```python
# browser_config.py
from playwright.sync_api import sync_playwright
import time
import random

class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    
    def setup_browser(self):
        """Setup headless browser with realistic configuration"""
        self.playwright = sync_playwright().start()
        
        # Realistic browser configuration
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
        
        self.browser = self.playwright.chromium.launch(
            headless=False,  # Start with visible browser for debugging
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-extensions",
                "--disable-plugins"
            ]
        )
        
        self.context = self.browser.new_context(
            user_agent=random.choice(user_agents),
            viewport={'width': 1920, 'height': 1080},
            java_script_enabled=True,
            images_enabled=True
        )
        
        # Override navigator.webdriver
        self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false,
            });
        """)
        
        self.page = self.context.new_page()
    
    def navigate_to_live_page(self):
        """Navigate to the live streaming page"""
        url = "https://www.gelonghui.com/live?channelId=all"
        self.page.goto(url, wait_until="networkidle")
        
        # Wait for JavaScript to load
        time.sleep(3)
        
        # Handle any popups or overlays
        try:
            self.page.wait_for_selector("button.close", timeout=5000)
            self.page.click("button.close")
        except:
            pass
    
    def monitor_network_requests(self):
        """Monitor network requests for API discovery"""
        requests = []
        
        def handle_request(request):
            if any(pattern in request.url for pattern in ['/api/', '/v1/', '/v2/', 'ws://', 'wss://']):
                requests.append({
                    'url': request.url,
                    'method': request.method,
                    'headers': dict(request.headers),
                    'timestamp': time.time()
                })
        
        self.page.on("request", handle_request)
        return requests
```

#### 1.2 Dynamic Content Extraction

```python
# dynamic_scraper.py
import asyncio
from datetime import datetime
import json

class DynamicScraper:
    def __init__(self, browser_manager):
        self.browser = browser_manager
        self.network_requests = []
    
    async def extract_live_stream_data(self):
        """Extract live stream metadata"""
        page = self.browser.page
        
        # Wait for live stream elements to load
        await page.wait_for_selector(".live-stream-item", timeout=10000)
        
        # Extract stream information
        streams = await page.evaluate("""
            () => {
                const streamElements = document.querySelectorAll('.live-stream-item');
                return Array.from(streamElements).map(element => {
                    return {
                        stream_id: element.getAttribute('data-stream-id'),
                        title: element.querySelector('.stream-title')?.innerText || '',
                        description: element.querySelector('.stream-description')?.innerText || '',
                        viewer_count: element.querySelector('.viewer-count')?.innerText || '0',
                        start_time: element.getAttribute('data-start-time'),
                        status: element.getAttribute('data-status'),
                        thumbnail: element.querySelector('img')?.src || '',
                        hashtags: Array.from(element.querySelectorAll('.hashtag')).map(tag => tag.innerText)
                    };
                });
            }
        """)
        
        return streams
    
    async def extract_chat_messages(self):
        """Extract real-time chat messages"""
        page = self.browser.page
        
        # Monitor chat container for new messages
        messages = []
        
        chat_messages = await page.evaluate("""
            () => {
                const chatContainer = document.querySelector('.chat-container');
                const messageElements = chatContainer?.querySelectorAll('.chat-message') || [];
                
                return Array.from(messageElements).map(element => {
                    return {
                        message_id: element.getAttribute('data-message-id'),
                        user_id: element.getAttribute('data-user-id'),
                        username: element.querySelector('.username')?.innerText || '',
                        content: element.querySelector('.message-content')?.innerText || '',
                        timestamp: element.getAttribute('data-timestamp'),
                        message_type: element.getAttribute('data-type'),
                        likes: element.querySelector('.like-count')?.innerText || '0'
                    };
                });
            }
        """)
        
        return chat_messages
    
    async def monitor_real_time_updates(self, duration=60):
        """Monitor real-time updates over time"""
        start_time = time.time()
        updates = []
        
        while time.time() - start_time < duration:
            # Extract current state
            streams = await self.extract_live_stream_data()
            messages = await self.extract_chat_messages()
            
            updates.append({
                'timestamp': datetime.now().isoformat(),
                'streams': streams,
                'messages': messages,
                'network_requests': self.network_requests.copy()
            })
            
            # Wait before next update
            await asyncio.sleep(5)
        
        return updates
```

### Phase 2: API Discovery and Integration

#### 2.1 Runtime API Detection

```python
# api_discoverer.py
import requests
from urllib.parse import urlparse, parse_qs

class APIDiscoverer:
    def __init__(self, base_url="https://www.gelonghui.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def analyze_network_requests(self, network_requests):
        """Analyze captured network requests for API patterns"""
        api_endpoints = []
        
        for request in network_requests:
            url = request['url']
            
            # Check for API patterns
            if any(pattern in url for pattern in ['/api/', '/v1/', '/v2/', '/graphql']):
                parsed_url = urlparse(url)
                endpoint = {
                    'url': url,
                    'method': request['method'],
                    'path': parsed_url.path,
                    'query_params': parse_qs(parsed_url.query),
                    'headers': request['headers'],
                    'frequency': 1
                }
                api_endpoints.append(endpoint)
            
            # Check for WebSocket connections
            elif url.startswith(('ws://', 'wss://')):
                websocket_info = {
                    'url': url,
                    'type': 'websocket',
                    'headers': request['headers']
                }
                api_endpoints.append(websocket_info)
        
        return api_endpoints
    
    def test_api_endpoint(self, endpoint):
        """Test API endpoint for data extraction"""
        try:
            response = self.session.request(
                method=endpoint['method'],
                url=endpoint['url'],
                headers=endpoint.get('headers', {}),
                timeout=10
            )
            
            return {
                'status_code': response.status_code,
                'content_type': response.headers.get('Content-Type'),
                'data': response.json() if response.headers.get('Content-Type', '').startswith('application/json') else response.text[:500],
                'success': response.status_code == 200
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
```

#### 2.2 WebSocket Connection Handling

```python
# websocket_handler.py
import websockets
import asyncio
import json
import logging

class WebSocketHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.connection = None
        self.messages = []
    
    async def connect_to_websocket(self, ws_url, headers=None):
        """Connect to WebSocket and capture messages"""
        try:
            self.connection = await websockets.connect(
                ws_url,
                extra_headers=headers or {},
                ping_interval=20,
                ping_timeout=20
            )
            
            self.logger.info(f"Connected to WebSocket: {ws_url}")
            
            # Start message listener
            asyncio.create_task(self._message_listener())
            
            return True
        except Exception as e:
            self.logger.error(f"WebSocket connection failed: {e}")
            return False
    
    async def _message_listener(self):
        """Listen for WebSocket messages"""
        try:
            async for message in self.connection:
                message_data = {
                    'timestamp': time.time(),
                    'message': message,
                    'type': 'websocket'
                }
                self.messages.append(message_data)
                
                # Process message based on content
                await self._process_message(message)
        except websockets.exceptions.ConnectionClosed:
            self.logger.info("WebSocket connection closed")
        except Exception as e:
            self.logger.error(f"WebSocket error: {e}")
    
    async def _process_message(self, message):
        """Process incoming WebSocket messages"""
        try:
            # Try to parse as JSON
            data = json.loads(message)
            
            # Handle different message types
            if data.get('type') == 'live_update':
                await self._handle_live_update(data)
            elif data.get('type') == 'chat_message':
                await self._handle_chat_message(data)
            elif data.get('type') == 'hashtag_update':
                await self._handle_hashtag_update(data)
                
        except json.JSONDecodeError:
            # Handle non-JSON messages
            self.logger.debug(f"Non-JSON message: {message}")
    
    async def _handle_live_update(self, data):
        """Handle live stream updates"""
        self.logger.info(f"Live update: {data.get('stream_id')}")
        # Process live stream data
    
    async def _handle_chat_message(self, data):
        """Handle chat messages"""
        self.logger.info(f"Chat message: {data.get('content')}")
        # Process chat message data
    
    async def _handle_hashtag_update(self, data):
        """Handle hashtag updates"""
        self.logger.info(f"Hashtag update: {data.get('hashtags')}")
        # Process hashtag data
    
    async def send_message(self, message):
        """Send message via WebSocket"""
        if self.connection:
            await self.connection.send(json.dumps(message))
    
    async def disconnect(self):
        """Disconnect from WebSocket"""
        if self.connection:
            await self.connection.close()
```

### Phase 3: Anti-Scraping Bypass Implementation

#### 3.1 Advanced Bot Detection Bypass

```python
# anti_detection.py
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class AntiDetection:
    @staticmethod
    def setup_stealth_driver():
        """Setup Chrome driver with stealth configuration"""
        options = Options()
        
        # Basic stealth options
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")  # Speed up loading
        
        # Window size and position
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--window-position=0,0")
        
        # User agent rotation
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
        
        options.add_argument(f"--user-agent={random.choice(user_agents)}")
        
        driver = webdriver.Chrome(options=options)
        
        # Execute stealth scripts
        driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false,
            });
        """)
        
        driver.execute_script("""
            window.chrome = {
                runtime: {},
            };
        """)
        
        return driver
    
    @staticmethod
    def human_like_interaction(driver):
        """Simulate human-like mouse movements and clicks"""
        actions = webdriver.ActionChains(driver)
        
        # Random mouse movements
        for _ in range(random.randint(3, 7)):
            x_offset = random.randint(-100, 100)
            y_offset = random.randint(-100, 100)
            actions.move_by_offset(x_offset, y_offset)
            actions.pause(random.uniform(0.1, 0.5))
        
        actions.perform()
        
        # Random scrolling
        scroll_amount = random.randint(100, 500)
        driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
        
        # Random wait
        time.sleep(random.uniform(1, 3))
    
    @staticmethod
    def handle_captcha(driver):
        """Handle CAPTCHA challenges"""
        try:
            # Check for CAPTCHA
            captcha_element = driver.find_element(By.XPATH, "//*[contains(text(), 'captcha') or contains(@class, 'captcha')]")
            if captcha_element:
                print("CAPTCHA detected - manual intervention required")
                return False
        except:
            pass
        
        return True
```

#### 3.2 Rate Limiting and Request Management

```python
# rate_limiter.py
import time
import random
from collections import deque
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, requests_per_minute=30, burst_size=5):
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.request_times = deque()
        self.last_reset = datetime.now()
    
    def wait_if_needed(self):
        """Wait if rate limit is exceeded"""
        now = datetime.now()
        
        # Clean old requests (older than 1 minute)
        while self.request_times and now - self.request_times[0] > timedelta(minutes=1):
            self.request_times.popleft()
        
        # Check if we need to wait
        if len(self.request_times) >= self.requests_per_minute:
            # Calculate wait time
            oldest_request = self.request_times[0]
            wait_time = 60 - (now - oldest_request).total_seconds()
            
            if wait_time > 0:
                print(f"Rate limit reached. Waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)
        
        # Add current request
        self.request_times.append(now)
    
    def random_delay(self, min_delay=1, max_delay=5):
        """Add random delay between requests"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def human_like_timing(self):
        """Simulate human-like request timing"""
        # Random delay between 2-8 seconds
        delay = random.uniform(2, 8)
        time.sleep(delay)
        
        # Occasionally longer delay (like reading content)
        if random.random() < 0.2:  # 20% chance
            extra_delay = random.uniform(10, 30)
            time.sleep(extra_delay)
```

### Phase 4: Data Processing and Analysis

#### 4.1 Hashtag Analysis Engine

```python
# hashtag_analyzer.py
import re
import jieba
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import logging

class HashtagAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.hashtag_frequency = Counter()
        self.hashtag_timeline = defaultdict(list)
        self.trending_threshold = 5
    
    def extract_hashtags(self, text):
        """Extract hashtags from text"""
        # Chinese hashtag pattern: #话题#
        chinese_pattern = r'#([^#\s]+)#'
        # English hashtag pattern: #topic
        english_pattern = r'(?<!\w)#([A-Za-z0-9_]+)'
        
        chinese_hashtags = re.findall(chinese_pattern, text)
        english_hashtags = re.findall(english_pattern, text)
        
        return chinese_hashtags + english_hashtags
    
    def analyze_content(self, content):
        """Analyze content for hashtags and keywords"""
        hashtags = self.extract_hashtags(content)
        
        # Update frequency
        for hashtag in hashtags:
            self.hashtag_frequency[hashtag] += 1
            self.hashtag_timeline[hashtag].append(datetime.now())
        
        # Extract keywords using jieba for Chinese text
        if any('\u4e00' <= char <= '\u9fff' for char in content):
            keywords = jieba.lcut(content)
            # Filter out stop words and short words
            keywords = [word for word in keywords if len(word) > 1 and word not in self._get_stop_words()]
        else:
            # English keyword extraction
            keywords = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        
        return {
            'hashtags': hashtags,
            'keywords': keywords,
            'timestamp': datetime.now()
        }
    
    def get_trending_hashtags(self, time_window_hours=1):
        """Get trending hashtags within time window"""
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        trending = []
        for hashtag, timestamps in self.hashtag_timeline.items():
            recent_count = sum(1 for t in timestamps if t > cutoff_time)
            
            if recent_count >= self.trending_threshold:
                trending.append({
                    'hashtag': hashtag,
                    'frequency': recent_count,
                    'trend_score': recent_count / time_window_hours
                })
        
        # Sort by trend score
        trending.sort(key=lambda x: x['trend_score'], reverse=True)
        return trending
    
    def _get_stop_words(self):
        """Get Chinese stop words"""
        return {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看',
            '好', '自己', '这', '那', '来', '他', '她', '它', '们', '这个', '那个'
        }
    
    def generate_report(self):
        """Generate analysis report"""
        trending = self.get_trending_hashtags()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_hashtags': len(self.hashtag_frequency),
            'top_hashtags': self.hashtag_frequency.most_common(10),
            'trending_hashtags': trending,
            'analysis_summary': {
                'high_frequency_threshold': self.trending_threshold,
                'time_window_hours': 1,
                'total_analyzed_items': sum(self.hashtag_frequency.values())
            }
        }
        
        return report
```

#### 4.2 Sentiment Analysis Integration

```python
# sentiment_analyzer.py
from textblob import TextBlob
import jieba.analyse
import logging

class SentimentAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of text"""
        # Check if Chinese text
        if any('\u4e00' <= char <= '\u9fff' for char in text):
            return self._analyze_chinese_sentiment(text)
        else:
            return self._analyze_english_sentiment(text)
    
    def _analyze_english_sentiment(self, text):
        """Analyze sentiment for English text"""
        blob = TextBlob(text)
        
        return {
            'polarity': blob.sentiment.polarity,  # -1 to 1
            'subjectivity': blob.sentiment.subjectivity,  # 0 to 1
            'sentiment_label': self._get_sentiment_label(blob.sentiment.polarity),
            'confidence': abs(blob.sentiment.polarity)
        }
    
    def _analyze_chinese_sentiment(self, text):
        """Analyze sentiment for Chinese text using keywords"""
        # Simple keyword-based sentiment analysis for Chinese
        positive_words = ['好', '棒', '赞', '喜欢', '支持', '成功', '上涨', '利好']
        negative_words = ['差', '坏', '讨厌', '反对', '失败', '下跌', '利空', '问题']
        
        positive_score = sum(1 for word in positive_words if word in text)
        negative_score = sum(1 for word in negative_words if word in text)
        
        total_score = positive_score - negative_score
        
        # Normalize to -1 to 1 range
        max_possible = max(len(positive_words), len(negative_words))
        normalized_score = total_score / max_possible if max_possible > 0 else 0
        
        return {
            'polarity': normalized_score,
            'subjectivity': 0.5,  # Simplified for Chinese
            'sentiment_label': self._get_sentiment_label(normalized_score),
            'confidence': abs(normalized_score),
            'positive_words': positive_score,
            'negative_words': negative_score
        }
    
    def _get_sentiment_label(self, polarity):
        """Get sentiment label from polarity score"""
        if polarity > 0.1:
            return 'positive'
        elif polarity < -0.1:
            return 'negative'
        else:
            return 'neutral'
    
    def analyze_content_sentiment(self, content_items):
        """Analyze sentiment of multiple content items"""
        sentiments = []
        
        for item in content_items:
            text = item.get('content', '') or item.get('message', '') or item.get('title', '')
            if text:
                sentiment = self.analyze_sentiment(text)
                sentiment.update({
                    'content_id': item.get('id'),
                    'timestamp': item.get('timestamp'),
                    'source': item.get('source', 'unknown')
                })
                sentiments.append(sentiment)
        
        return sentiments
```

## Database Schema Implementation

### Enhanced Database Models

```python
# models/enhanced_models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class LiveStream(Base):
    __tablename__ = 'live_streams'
    
    id = Column(Integer, primary_key=True)
    stream_id = Column(String(100), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    status = Column(String(50))
    viewer_count = Column(Integer, default=0)
    platform_source = Column(String(100))
    stream_url = Column(Text)
    thumbnail_url = Column(Text)
    hashtags = Column(JSON)  # Store as JSON array
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'stream_id': self.stream_id,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'viewer_count': self.viewer_count,
            'platform_source': self.platform_source,
            'stream_url': self.stream_url,
            'thumbnail_url': self.thumbnail_url,
            'hashtags': self.hashtags,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True)
    message_id = Column(String(100), unique=True)
    stream_id = Column(String(100), nullable=False)
    user_id = Column(String(100))
    username = Column(String(200))
    content = Column(Text, nullable=False)
    message_type = Column(String(50))
    timestamp = Column(DateTime)
    sentiment_score = Column(Float)
    sentiment_label = Column(String(20))
    likes = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'message_id': self.message_id,
            'stream_id': self.stream_id,
            'user_id': self.user_id,
            'username': self.username,
            'content': self.content,
            'message_type': self.message_type,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'sentiment_score': self.sentiment_score,
            'sentiment_label': self.sentiment_label,
            'likes': self.likes,
            'is_deleted': self.is_deleted,
            'created_at': self.created_at.isoformat()
        }

class TrendingTopic(Base):
    __tablename__ = 'trending_topics'
    
    id = Column(Integer, primary_key=True)
    topic_name = Column(String(200), nullable=False)
    score = Column(Float, default=0.0)
    frequency = Column(Integer, default=0)
    timestamp = Column(DateTime)
    source_stream = Column(String(100))
    hashtag_count = Column(Integer, default=0)
    sentiment_score = Column(Float)
    sentiment_label = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'topic_name': self.topic_name,
            'score': self.score,
            'frequency': self.frequency,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'source_stream': self.source_stream,
            'hashtag_count': self.hashtag_count,
            'sentiment_score': self.sentiment_score,
            'sentiment_label': self.sentiment_label,
            'created_at': self.created_at.isoformat()
        }
```

## Deployment and Monitoring

### Docker Configuration

```dockerfile
# Dockerfile for scraping service
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV CHROMIUM_BIN=/usr/bin/chromium

# Run the application
CMD ["python", "-m", "glonghui_analysis.main"]
```

### Monitoring and Logging

```python
# monitoring.py
import logging
import time
from datetime import datetime
import psutil
import requests

class SystemMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.start_time = time.time()
    
    def log_system_metrics(self):
        """Log system resource usage"""
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        
        self.logger.info(f"System Metrics - CPU: {cpu_usage}%, Memory: {memory_usage}%, Disk: {disk_usage}%")
    
    def log_scraping_metrics(self, scraped_items, errors):
        """Log scraping performance metrics"""
        uptime = time.time() - self.start_time
        items_per_hour = (scraped_items / uptime) * 3600 if uptime > 0 else 0
        
        self.logger.info(f"Scraping Metrics - Items: {scraped_items}, Errors: {errors}, Rate: {items_per_hour:.2f}/hour, Uptime: {uptime:.2f}s")
    
    def health_check(self):
        """Perform health check on the system"""
        try:
            # Check if main services are running
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                self.logger.info("Health check passed")
                return True
        except:
            self.logger.error("Health check failed")
            return False
```

This comprehensive technical implementation guide provides a complete roadmap for building a robust data extraction and analysis system for the 格隆汇 live streaming platform, based on our detailed website analysis findings.