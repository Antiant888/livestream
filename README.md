# Gelonghui News Scraper

A comprehensive web scraping application that fetches real-time news data from the Gelonghui API, stores it in PostgreSQL, and provides a web UI for analysis and visualization.

## 🎯 Features

### Core Functionality
- **Real-time News Scraping**: Incremental timestamp-based scraping from Gelonghui API
- **Data Parsing**: Advanced regex-based extraction of hashtags, stocks, and content
- **Database Storage**: PostgreSQL with SQLAlchemy ORM for persistent storage
- **Web Dashboard**: Streamlit-based analytics dashboard with real-time visualizations
- **Scheduled Scraping**: APScheduler for automated periodic data collection

### Data Analysis
- **Hashtag Frequency Analysis**: Track trending topics and hashtags
- **Engagement Metrics**: Analyze read counts, shares, comments, and likes
- **Stock Mentions**: Monitor stock symbols and market mentions
- **Time-based Trends**: Visualize data patterns over time
- **Content Classification**: Categorize news by topics and engagement

### Technical Features
- **Rate Limiting**: Respectful API usage with built-in rate limiting
- **Error Handling**: Comprehensive error handling and retry mechanisms
- **Logging**: Detailed logging for monitoring and debugging
- **Docker Support**: Containerized deployment ready
- **Railway Deployment**: One-click deployment to Railway.app

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        DEPLOYMENT LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│  Railway.app (Multi-service deployment)                         │
│  ├── Scraper Service (Python)                                   │
│  ├── Web UI Service (Streamlit)                                 │
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
│  │   ├── Dashboard (Streamlit)                                  │
│  │   ├── Data Visualization (Plotly)                            │
│  │   └── API Endpoints                                          │
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

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL database
- Git

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd glonghui-news-scraper
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your database URL and other settings
```

4. **Initialize database**
```bash
python main.py setup
```

5. **Test connections**
```bash
python main.py test --api --database
```

### Running the Application

#### Option 1: Run Scraper (Daemon Mode)
```bash
python main.py run --scraper --interval 5
```

#### Option 2: Run Web Dashboard
```bash
python main.py run --dashboard
```

#### Option 3: Run Both (Separate Terminals)
```bash
# Terminal 1: Start scraper
python main.py run --scraper

# Terminal 2: Start dashboard
python main.py run --dashboard
```

### Using Docker

#### Build and Run
```bash
# Build the image
docker build -t glonghui-scraper .

# Run the container
docker run -p 8501:8501 \
  -e DATABASE_URL="postgresql://user:password@host:port/db" \
  glonghui-scraper
```

#### Docker Compose (Development)
```bash
docker-compose up -d
```

## 📊 Web Dashboard

Access the web dashboard at `http://localhost:8501` to view:

- **Real-time Metrics**: Total news, top hashtags, engagement scores
- **Hashtag Analysis**: Frequency charts and trending topics
- **Engagement Analysis**: Top engaged items and metrics breakdown
- **Stock Analysis**: Stock mentions and market distribution
- **News Feed**: Latest news with filters and pagination

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | `sqlite:///news_data.db` |
| `SCRAPING_INTERVAL_MINUTES` | Scraping interval | `1` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `API_BASE_URL` | Gelonghui API base URL | `https://www.gelonghui.com` |
| `USER_AGENT` | User agent for API requests | `Mozilla/5.0...` |

### Database Schema

The application creates the following tables:

- **news_items**: Main news content with engagement metrics
- **stocks**: Related stock information
- **hashtags**: Extracted hashtags with frequencies
- **trends**: Calculated trend data

## 📈 Data Analysis Features

### Hashtag Analysis
- **Frequency Tracking**: Count hashtag occurrences over time
- **Trend Detection**: Identify trending topics
- **Time-based Analysis**: Visualize hashtag popularity over time periods

### Engagement Analysis
- **Engagement Score**: Weighted scoring based on reads, shares, comments, likes
- **Top Content**: Identify most engaging news items
- **Engagement Patterns**: Analyze engagement over time

### Stock Analysis
- **Mention Tracking**: Count stock symbol mentions
- **Market Distribution**: Analyze mentions by market (SH, SZ, HK, US)
- **Stock Trends**: Track stock mentions over time

## 🚀 Deployment

### Railway.app Deployment

1. **Create Railway Account**: [railway.app](https://railway.app)
2. **Deploy from GitHub**: Connect your repository
3. **Configure Environment**: Set environment variables
4. **Deploy**: Railway will automatically deploy using `railway.json`

### Docker Deployment

```bash
# Build and push to registry
docker build -t your-registry/glonghui-scraper:latest .
docker push your-registry/glonghui-scraper:latest

# Deploy to your container platform
kubectl apply -f kubernetes/deployment.yaml
```

### Heroku Deployment

```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set DATABASE_URL="your-database-url"

# Deploy
git push heroku main
```

## 🛠️ Development

### Project Structure

```
glonghui-news-scraper/
├── scraper/                    # Core scraping functionality
│   ├── api_client.py          # Gelonghui API client
│   ├── data_parser.py         # Data parsing and extraction
│   ├── database.py            # Database operations
│   ├── scheduler.py           # Scraping scheduler
│   └── models/                # SQLAlchemy models
├── web_ui/                     # Streamlit web interface
│   ├── app.py                 # Main dashboard application
│   └── visualizations.py      # Chart generation
├── tests/                      # Unit tests
├── scripts/                    # Utility scripts
├── docs/                       # Documentation
├── requirements.txt            # Python dependencies
├── Dockerfile                 # Docker configuration
├── railway.json               # Railway deployment config
└── main.py                    # CLI entry point
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_api_client.py

# Run with coverage
pytest --cov=scraper tests/
```

### Code Style

```bash
# Format code
black .

# Check type hints
mypy scraper/

# Lint code
flake8 scraper/
```

## 🔍 Monitoring and Maintenance

### Health Checks

The application provides health check endpoints:
- Scraper: `/health`
- Web UI: `/_stcore/health`

### Logging

Logs are written to:
- File: `scraper.log`
- Console: Standard output

### Database Maintenance

```bash
# Clean up old data (keep 30 days)
python main.py cleanup --days 30

# Show system status
python main.py status
```

## 📋 API Reference

### Gelonghui API Endpoints

- **Live News**: `GET /api/live-channels/all/lives/v4`
  - Parameters: `category`, `limit`, `timestamp`
  - Returns: JSON with news items

### Internal API

The scraper provides internal endpoints for monitoring:
- **Health Check**: `GET /health`
- **Status**: `GET /status`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for your changes
5. Run tests and ensure they pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check `DATABASE_URL` environment variable
   - Ensure PostgreSQL is running
   - Verify credentials

2. **API Rate Limiting**
   - Increase scraping interval
   - Check API status
   - Review rate limiting settings

3. **Docker Issues**
   - Ensure Docker is installed and running
   - Check port availability
   - Verify environment variables

### Getting Help

- Check the [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
- Review logs in `scraper.log`
- Create an issue on GitHub

## 📞 Support

For support and questions:
- Create a GitHub issue
- Check the documentation in `/docs`
- Review the troubleshooting guide

## 🙏 Acknowledgments

- Gelonghui for providing the news API
- SQLAlchemy team for the excellent ORM
- Streamlit team for the fantastic dashboard framework
- APScheduler team for reliable scheduling

---

**Note**: This application is designed for educational and analytical purposes. Please respect the Gelonghui API terms of service and rate limits.