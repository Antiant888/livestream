# Gelonghui Real-time News Scraper - Complete Project Plan

## Project Overview

Build a comprehensive web scraping application that fetches real-time news data from the Gelonghui API, stores it in PostgreSQL, and provides a web UI for analysis and visualization.

## Project Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        DEPLOYMENT LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│  Railway.app (Multi-service deployment)                         │
│  ├── Scraper Service (Python)                                   │
│  ├── Web UI Service (Streamlit/Flask)                           │
│  ├── PostgreSQL Database                                        │
│  └── Redis (Optional: Caching)                                  │
├─────────────────────────────────────────────────────────────────┤
│                        APPLICATION LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│  ├── Scraper Module                                             │
│  │   ├── API Client (requests)                                  │
│  │   ├── Data Parser (regex, JSON)                              │
│  │   ├── Database Writer (SQLAlchemy)                           │
│  │   └── Scheduler (APScheduler)                                │
│  ├── Web UI Module                                              │
│  │   ├── Dashboard (Streamlit/Flask)                            │
│  │   ├── Data Visualization (Plotly/Matplotlib)                 │
│  │   └── API Endpoints (FastAPI/Flask)                          │
│  └── Analysis Module                                            │
│      ├── Hashtag Extraction (regex)                             │
│      ├── Sentiment Analysis (textblob)                          │
│      └── Trend Analysis (pandas)                                │
├─────────────────────────────────────────────────────────────────┤
│                        DATA LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL Database                                            │
│  ├── news_items (main table)                                    │
│  ├── stocks (related stocks)                                    │
│  ├── hashtags (extracted hashtags)                              │
│  ├── trends (calculated trends)                                 │
│  └── engagement_metrics (read, share, comment counts)           │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Backend (Scraper & API)
- **Python 3.9+**
- **requests** - HTTP client for API calls
- **SQLAlchemy** - ORM for database operations
- **APScheduler** - Task scheduling
- **regex** - Advanced text parsing
- **python-dotenv** - Environment variables

### Frontend (Web UI)
- **Streamlit** - Simple, fast web UI (Recommended)
- **Flask** - Alternative web framework
- **Plotly** - Interactive data visualization
- **Pandas** - Data manipulation and analysis

### Database
- **PostgreSQL** - Primary database
- **Redis** - Optional caching (future enhancement)

### Deployment
- **Railway.app** - Cloud deployment platform
- **Docker** - Containerization
- **GitHub** - Version control and CI/CD

## Project Structure

```
glonghui-news-scraper/
├── README.md                           # Project documentation
├── requirements.txt                      # Python dependencies
├── .gitignore                           # Git ignore file
├── docker-compose.yml                   # Local development setup
├── Dockerfile                          # Production container
├── railway.json                        # Railway deployment config
├── scraper/                            # Main scraper module
│   ├── __init__.py
│   ├── config.py                       # Configuration management
│   ├── api_client.py                   # Gelonghui API client
│   ├── data_parser.py                  # Data parsing and extraction
│   ├── database.py                     # Database operations
│   ├── scheduler.py                    # Task scheduling
│   ├── models/                         # Database models
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── news_item.py
│   │   ├── stock.py
│   │   ├── hashtag.py
│   │   └── trend.py
│   └── utils/                          # Utility functions
│       ├── __init__.py
│       ├── logger.py
│       ├── regex_patterns.py
│       └── helpers.py
├── web_ui/                             # Web interface
│   ├── __init__.py
│   ├── app.py                          # Main Streamlit/Flask app
│   ├── dashboard.py                    # Dashboard components
│   ├── visualizations.py               # Chart generation
│   ├── api.py                          # API endpoints
│   └── templates/                      # HTML templates (Flask)
│       └── index.html
├── analysis/                           # Data analysis module
│   ├── __init__.py
│   ├── hashtag_analyzer.py             # Hashtag frequency analysis
│   ├── sentiment_analyzer.py           # Sentiment analysis
│   └── trend_analyzer.py               # Trend detection
├── tests/                              # Unit tests
│   ├── __init__.py
│   ├── test_api_client.py
│   ├── test_data_parser.py
│   └── test_database.py
├── scripts/                            # Utility scripts
│   ├── setup_db.py                     # Database setup script
│   ├── migrate.py                      # Database migrations
│   └── seed_data.py                    # Sample data seeding
└── docs/                               # Documentation
    ├── API_SPECIFICATION.md
    ├── DEPLOYMENT_GUIDE.md
    └── ARCHITECTURE.md
```

## Implementation Phases

### Phase 1: Foundation Setup (Week 1)

#### Day 1-2: Project Initialization
- [ ] Create GitHub repository
- [ ] Initialize Python project structure
- [ ] Set up virtual environment and dependencies
- [ ] Create basic configuration files

#### Day 3-4: Database Design
- [ ] Design PostgreSQL schema
- [ ] Create SQLAlchemy models
- [ ] Set up database connection
- [ ] Create migration scripts

#### Day 5-7: API Client Development
- [ ] Implement Gelonghui API client
- [ ] Add error handling and retry logic
- [ ] Implement rate limiting
- [ ] Add logging and monitoring

### Phase 2: Core Scraping Logic (Week 2)

#### Day 1-3: Data Parsing
- [ ] Implement JSON response parsing
- [ ] Create regex patterns for hashtag extraction
- [ ] Implement stock symbol detection
- [ ] Add content cleaning and normalization

#### Day 4-5: Database Integration
- [ ] Implement data insertion logic
- [ ] Add duplicate detection and handling
- [ ] Create update mechanisms for existing records
- [ ] Implement data validation

#### Day 6-7: Scheduling System
- [ ] Set up APScheduler for periodic scraping
- [ ] Implement incremental timestamp tracking
- [ ] Add graceful shutdown handling
- [ ] Create monitoring and alerting

### Phase 3: Web UI Development (Week 3)

#### Day 1-3: Dashboard Design
- [ ] Create main dashboard layout
- [ ] Implement data display components
- [ ] Add filtering and search functionality
- [ ] Create responsive design

#### Day 4-5: Visualization
- [ ] Implement hashtag frequency charts
- [ ] Create engagement trend visualizations
- [ ] Add time-based analysis charts
- [ ] Implement interactive elements

#### Day 6-7: API Endpoints
- [ ] Create RESTful API endpoints
- [ ] Add data export functionality
- [ ] Implement authentication (optional)
- [ ] Add API documentation

### Phase 4: Analysis and Optimization (Week 4)

#### Day 1-3: Advanced Analysis
- [ ] Implement sentiment analysis
- [ ] Create trend detection algorithms
- [ ] Add predictive analytics (optional)
- [ ] Implement data quality checks

#### Day 4-5: Performance Optimization
- [ ] Optimize database queries
- [ ] Implement caching strategies
- [ ] Add data compression
- [ ] Optimize API response times

#### Day 6-7: Testing and Documentation
- [ ] Write comprehensive unit tests
- [ ] Create integration tests
- [ ] Write user documentation
- [ ] Create deployment documentation

### Phase 5: Deployment (Week 5)

#### Day 1-3: Railway Setup
- [ ] Create Railway account
- [ ] Set up PostgreSQL database
- [ ] Configure environment variables
- [ ] Deploy scraper service

#### Day 4-5: Production Deployment
- [ ] Deploy web UI service
- [ ] Configure domain and SSL
- [ ] Set up monitoring and logging
- [ ] Test production environment

#### Day 6-7: Final Testing
- [ ] Perform end-to-end testing
- [ ] Load testing and performance validation
- [ ] Security review and hardening
- [ ] Final documentation updates

## Database Schema Design

### Table: news_items
```sql
CREATE TABLE news_items (
    id SERIAL PRIMARY KEY,
    glonghui_id VARCHAR(100) UNIQUE NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    content_prefix VARCHAR(100),
    create_timestamp BIGINT NOT NULL,
    update_timestamp BIGINT,
    level INTEGER DEFAULT 0,
    route VARCHAR(500),
    close_comment BOOLEAN DEFAULT FALSE,
    read_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    favorite_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Table: stocks
```sql
CREATE TABLE stocks (
    id SERIAL PRIMARY KEY,
    news_item_id INTEGER REFERENCES news_items(id) ON DELETE CASCADE,
    market VARCHAR(10),
    code VARCHAR(20),
    name VARCHAR(100),
    can_click BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Table: hashtags
```sql
CREATE TABLE hashtags (
    id SERIAL PRIMARY KEY,
    news_item_id INTEGER REFERENCES news_items(id) ON DELETE CASCADE,
    hashtag_text VARCHAR(100) NOT NULL,
    frequency INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(news_item_id, hashtag_text)
);
```

### Table: trends
```sql
CREATE TABLE trends (
    id SERIAL PRIMARY KEY,
    hashtag_text VARCHAR(100) NOT NULL,
    frequency INTEGER DEFAULT 0,
    trend_score DECIMAL(10,2) DEFAULT 0.0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    time_window VARCHAR(20) DEFAULT '1h' -- '1h', '24h', '7d'
);
```

## Key Implementation Details

### 1. API Client Implementation
```python
class GelonghuiAPIClient:
    def __init__(self, base_url="https://www.gelonghui.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; GelonghuiScraper/1.0)',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://www.gelonghui.com/'
        })
        self.rate_limiter = RateLimiter(requests_per_minute=60)
    
    def get_live_news(self, category="all", limit=15, timestamp=None):
        """Fetch live news with incremental timestamp"""
        params = {
            'category': category,
            'limit': limit
        }
        if timestamp:
            params['timestamp'] = timestamp
        
        self.rate_limiter.wait_if_needed()
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/live-channels/all/lives/v4",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
```

### 2. Data Parsing with Regex
```python
class DataParser:
    def __init__(self):
        self.hashtag_patterns = [
            r'#([^#\s]+)#',  # Chinese hashtags: #话题#
            r'(?<!\w)#([A-Za-z0-9_]+)'  # English hashtags: #topic
        ]
        self.stock_pattern = r'([A-Z]{1,2})\s*(\d{4,6})\.(SH|SZ|HK)'  # Stock symbols
    
    def extract_hashtags(self, text):
        """Extract hashtags from content"""
        hashtags = []
        for pattern in self.hashtag_patterns:
            matches = re.findall(pattern, text)
            hashtags.extend(matches)
        return list(set(hashtags))  # Remove duplicates
    
    def extract_stocks(self, related_stocks):
        """Extract stock information from API response"""
        stocks = []
        if related_stocks:
            for stock in related_stocks:
                stocks.append({
                    'market': stock.get('market'),
                    'code': stock.get('code'),
                    'name': stock.get('name'),
                    'can_click': stock.get('canClick', False)
                })
        return stocks
```

### 3. Database Operations
```python
class DatabaseManager:
    def __init__(self, database_url):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
    
    def insert_news_item(self, news_data):
        """Insert or update news item"""
        session = self.Session()
        try:
            # Check if item exists
            existing = session.query(NewsItem).filter_by(
                glonghui_id=news_data['id']
            ).first()
            
            if existing:
                # Update existing item
                for key, value in news_data.items():
                    setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
            else:
                # Insert new item
                news_item = NewsItem(**news_data)
                session.add(news_item)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Database operation failed: {e}")
            return False
        finally:
            session.close()
```

### 4. Scheduling System
```python
class ScraperScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.last_timestamp = self.get_last_timestamp()
    
    def start(self):
        """Start the scraping scheduler"""
        self.scheduler.add_job(
            self.scrape_news,
            'interval',
            seconds=int(os.getenv('SCRAPING_INTERVAL', 30)),
            id='news_scraper',
            replace_existing=True
        )
        self.scheduler.start()
        logger.info("Scraper scheduler started")
    
    def scrape_news(self):
        """Main scraping job"""
        try:
            api_client = GelonghuiAPIClient()
            parser = DataParser()
            db_manager = DatabaseManager(os.getenv('DATABASE_URL'))
            
            # Fetch new items
            data = api_client.get_live_news(
                category='all',
                limit=15,
                timestamp=self.last_timestamp
            )
            
            if data and 'result' in data:
                for item in data['result']:
                    # Parse and process item
                    parsed_data = parser.parse_news_item(item)
                    
                    # Insert into database
                    db_manager.insert_news_item(parsed_data)
                    
                    # Update timestamp
                    self.last_timestamp = max(
                        self.last_timestamp,
                        item.get('createTimestamp', 0)
                    )
                    
                    # Extract and store hashtags
                    hashtags = parser.extract_hashtags(item.get('content', ''))
                    db_manager.insert_hashtags(item['id'], hashtags)
            
            logger.info(f"Scraped {len(data.get('result', []))} new items")
            
        except Exception as e:
            logger.error(f"Scraping job failed: {e}")
```

### 5. Web UI with Streamlit
```python
def create_dashboard():
    """Create main dashboard"""
    st.set_page_config(
        page_title="Gelonghui News Analytics",
        page_icon="📰",
        layout="wide"
    )
    
    st.title("📰 Gelonghui Real-time News Analytics")
    
    # Sidebar filters
    with st.sidebar:
        st.header("Filters")
        time_range = st.selectbox(
            "Time Range",
            ["Last 1 hour", "Last 24 hours", "Last 7 days"]
        )
        category = st.selectbox(
            "Category",
            ["All", "Financial", "Technology", "International"]
        )
    
    # Main content
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total News Items",
            get_total_news_count(time_range)
        )
    
    with col2:
        st.metric(
            "Top Hashtag",
            get_top_hashtag(time_range)
        )
    
    with col3:
        st.metric(
            "Avg Engagement",
            f"{get_avg_engagement(time_range):.1f}%"
        )
    
    # Charts
    st.subheader("📈 Hashtag Frequency")
    hashtag_chart = create_hashtag_chart(time_range)
    st.plotly_chart(hashtag_chart, use_container_width=True)
    
    st.subheader("🔥 Top Engaged Items")
    top_items = get_top_engaged_items(time_range)
    st.dataframe(top_items)
```

## Deployment Configuration

### Railway.json Configuration
```json
{
  "name": "glonghui-news-scraper",
  "services": [
    {
      "name": "scraper",
      "source": "./scraper",
      "env": {
        "DATABASE_URL": {
          "fromService": {
            "service": "database",
            "property": "url"
          }
        },
        "SCRAPING_INTERVAL": "30",
        "LOG_LEVEL": "INFO"
      }
    },
    {
      "name": "web-ui",
      "source": "./web_ui",
      "env": {
        "DATABASE_URL": {
          "fromService": {
            "service": "database",
            "property": "url"
          }
        },
        "PORT": "8080"
      }
    },
    {
      "name": "database",
      "source": {
        "type": "add-on",
        "addonType": "postgresql"
      }
    }
  ]
}
```

### Docker Configuration
```dockerfile
# Scraper Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scraper/ ./scraper/
COPY scripts/ ./scripts/

CMD ["python", "-m", "scraper.scheduler"]
```

## Ethical Considerations and Best Practices

### 1. Rate Limiting
- Respect API rate limits (60 requests/minute)
- Implement exponential backoff for failed requests
- Use appropriate delays between requests

### 2. Data Privacy
- Only collect publicly available data
- Don't store sensitive personal information
- Implement data retention policies

### 3. Error Handling
- Graceful handling of API failures
- Retry mechanisms with backoff
- Comprehensive logging for debugging

### 4. Monitoring
- Health checks for all services
- Performance monitoring
- Alerting for failures and anomalies

## Testing Strategy

### Unit Tests
- API client functionality
- Data parsing accuracy
- Database operations
- Regex pattern matching

### Integration Tests
- End-to-end scraping workflow
- Database integration
- Web UI functionality

### Performance Tests
- Load testing for API calls
- Database query performance
- Web UI response times

## Monitoring and Maintenance

### Key Metrics to Monitor
- Scraping success rate
- Database performance
- API response times
- Error rates and types

### Maintenance Tasks
- Regular database cleanup
- Log rotation
- Dependency updates
- Performance optimization

## Success Criteria

### Functional Requirements
- [ ] Successfully scrape Gelonghui API with incremental timestamps
- [ ] Parse and extract all required fields accurately
- [ ] Store data in PostgreSQL with proper relationships
- [ ] Handle duplicates and updates efficiently
- [ ] Display data in web UI with filters and visualizations
- [ ] Calculate hashtag frequencies and trends
- [ ] Show top engaged items based on metrics

### Non-Functional Requirements
- [ ] 99% uptime for scraping service
- [ ] Response time under 2 seconds for web UI
- [ ] Handle 1000+ concurrent users
- [ ] Data accuracy above 95%
- [ ] Graceful error handling and recovery

This comprehensive project plan provides a complete roadmap for building a production-ready web scraping application with real-time data processing, analysis, and visualization capabilities.