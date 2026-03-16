from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import List, Dict, Any

from .database.config import engine, get_db, init_db
from .scrapers.glonghui_scraper import GelonghuiScraper
from .scrapers.mock_scraper import MockScraper
from .analysis.hashtag_analyzer import HashtagAnalyzer
from .models.live_streams import LiveStream
from .models.stream_content import StreamContent
from .models.hashtags import Hashtag, TrendingTopic

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for background tasks
scraper_task = None
analyzer_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Initializing database...")
    init_db()
    
    # Start background tasks
    global scraper_task, analyzer_task
    scraper_task = asyncio.create_task(run_scraper())
    analyzer_task = asyncio.create_task(run_analyzer())
    
    yield
    
    # Shutdown
    if scraper_task:
        scraper_task.cancel()
    if analyzer_task:
        analyzer_task.cancel()
    
    logger.info("Application shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="格隆汇 Live Streaming Analysis API",
    description="API for scraping and analyzing 格隆汇 live streaming data",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "格隆汇 Live Streaming Analysis API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/streams")
async def get_live_streams(db: Session = Depends(get_db)):
    """Get all live streams"""
    try:
        streams = db.query(LiveStream).all()
        return {
            "streams": [
                {
                    "stream_id": stream.stream_id,
                    "title": stream.title,
                    "status": stream.status,
                    "viewer_count": stream.viewer_count,
                    "platform_source": stream.platform_source,
                    "thumbnail_url": stream.thumbnail_url,
                    "channel_name": stream.channel_name,
                    "start_time": stream.start_time,
                    "end_time": stream.end_time
                } for stream in streams
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/streams/{stream_id}/content")
async def get_stream_content(stream_id: str, db: Session = Depends(get_db)):
    """Get content for a specific stream"""
    try:
        content = db.query(StreamContent).filter(
            StreamContent.stream_id == stream_id
        ).order_by(StreamContent.timestamp.desc()).limit(100).all()
        
        return {
            "stream_id": stream_id,
            "content": [
                {
                    "content_id": c.content_id,
                    "timestamp": c.timestamp,
                    "content_type": c.content_type,
                    "text_content": c.text_content,
                    "hashtags": c.hashtags,
                    "mentions": c.mentions,
                    "sentiment_score": float(c.sentiment_score) if c.sentiment_score else None,
                    "username": c.username,
                    "message_type": c.message_type
                } for c in content
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hashtags/frequency")
async def get_hashtag_frequency(
    time_window: int = 24,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get hashtag frequency analysis"""
    try:
        analyzer = HashtagAnalyzer(db)
        results = await analyzer.analyze_hashtag_frequency(time_window, limit)
        
        return {
            "time_window": time_window,
            "limit": limit,
            "hashtags": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trends")
async def get_trending_topics(
    time_window: int = 24,
    min_frequency: int = 5,
    min_velocity: float = 0.5,
    db: Session = Depends(get_db)
):
    """Get trending topics"""
    try:
        analyzer = HashtagAnalyzer(db)
        trends = await analyzer.detect_trending_topics(time_window, min_frequency, min_velocity)
        
        return {
            "time_window": time_window,
            "min_frequency": min_frequency,
            "min_velocity": min_velocity,
            "trends": trends
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trends/sentiment")
async def get_sentiment_trends(
    time_window: int = 24,
    hashtag: str = None,
    db: Session = Depends(get_db)
):
    """Get sentiment analysis for trends"""
    try:
        analyzer = HashtagAnalyzer(db)
        sentiment_analysis = await analyzer.analyze_sentiment_trends(time_window, hashtag)
        
        return {
            "time_window": time_window,
            "hashtag_filter": hashtag,
            "sentiment_analysis": sentiment_analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/realtime")
async def get_real_time_stats(db: Session = Depends(get_db)):
    """Get real-time statistics"""
    try:
        analyzer = HashtagAnalyzer(db)
        stats = await analyzer.get_real_time_stats()
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scrape")
async def trigger_scraping(db: Session = Depends(get_db)):
    """Manually trigger scraping process"""
    try:
        async with GelonghuiScraper() as scraper:
            results = await scraper.scrape()
            
            # Save results to database
            for result in results:
                if result.get('stream_id'):
                    # Save stream data
                    stream = db.query(LiveStream).filter(
                        LiveStream.stream_id == result['stream_id']
                    ).first()
                    
                    if not stream:
                        stream = LiveStream(
                            stream_id=result['stream_id'],
                            title=result.get('title', ''),
                            viewer_count=result.get('viewer_count', 0),
                            status=result.get('status', 'scheduled'),
                            platform_source=result.get('platform_source', 'gelonghui'),
                            thumbnail_url=result.get('thumbnail_url'),
                            channel_id=result.get('channel_id'),
                            channel_name=result.get('channel_name')
                        )
                        db.add(stream)
                    else:
                        # Update existing stream
                        stream.title = result.get('title', stream.title)
                        stream.viewer_count = result.get('viewer_count', stream.viewer_count)
                        stream.status = result.get('status', stream.status)
                        stream.thumbnail_url = result.get('thumbnail_url', stream.thumbnail_url)
                        stream.channel_name = result.get('channel_name', stream.channel_name)
                
                elif result.get('content_type'):
                    # Save content data
                    content = StreamContent(
                        stream_id=result['stream_id'],
                        timestamp=result.get('timestamp', datetime.utcnow()),
                        content_type=result['content_type'],
                        text_content=result.get('text_content'),
                        hashtags=result.get('hashtags'),
                        mentions=result.get('mentions'),
                        sentiment_score=result.get('sentiment_score'),
                        user_id=result.get('user_id'),
                        username=result.get('username'),
                        message_type=result.get('message_type')
                    )
                    db.add(content)
            
            db.commit()
            
        return {
            "message": "Scraping completed successfully",
            "results_count": len(results)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def trigger_analysis(db: Session = Depends(get_db)):
    """Manually trigger analysis process"""
    try:
        analyzer = HashtagAnalyzer(db)
        
        # Run hashtag frequency analysis
        hashtag_analysis = await analyzer.analyze_hashtag_frequency()
        
        # Detect trending topics
        trending_topics = await analyzer.detect_trending_topics()
        
        # Save trending topics
        await analyzer.save_trending_topics(trending_topics)
        
        return {
            "message": "Analysis completed successfully",
            "hashtag_count": len(hashtag_analysis),
            "trending_topics_count": len(trending_topics)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scrape/mock")
async def trigger_mock_scraping(db: Session = Depends(get_db)):
    """Manually trigger mock data generation for testing"""
    try:
        async with MockScraper() as scraper:
            results = await scraper.scrape()
            
            # Save results to database
            for result in results:
                if result.get('stream_id'):
                    # Save stream data
                    stream = db.query(LiveStream).filter(
                        LiveStream.stream_id == result['stream_id']
                    ).first()
                    
                    if not stream:
                        stream = LiveStream(
                            stream_id=result['stream_id'],
                            title=result.get('title', ''),
                            viewer_count=result.get('viewer_count', 0),
                            status=result.get('status', 'scheduled'),
                            platform_source=result.get('platform_source', 'mock'),
                            thumbnail_url=result.get('thumbnail_url'),
                            channel_id=result.get('channel_id'),
                            channel_name=result.get('channel_name')
                        )
                        db.add(stream)
                    else:
                        # Update existing stream
                        stream.title = result.get('title', stream.title)
                        stream.viewer_count = result.get('viewer_count', stream.viewer_count)
                        stream.status = result.get('status', stream.status)
                        stream.thumbnail_url = result.get('thumbnail_url', stream.thumbnail_url)
                        stream.channel_name = result.get('channel_name', stream.channel_name)
                
                elif result.get('content_type'):
                    # Save content data
                    content = StreamContent(
                        stream_id=result['stream_id'],
                        timestamp=result.get('timestamp', datetime.utcnow()),
                        content_type=result['content_type'],
                        text_content=result.get('text_content'),
                        hashtags=result.get('hashtags'),
                        mentions=result.get('mentions'),
                        sentiment_score=result.get('sentiment_score'),
                        user_id=result.get('user_id'),
                        username=result.get('username'),
                        message_type=result.get('message_type')
                    )
                    db.add(content)
            
            db.commit()
            
        return {
            "message": "Mock data generation completed successfully",
            "results_count": len(results),
            "note": "Using mock data for testing and demonstration"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Background tasks
async def run_scraper():
    """Background task to run scraping periodically"""
    while True:
        try:
            logger.info("Starting scheduled scraping...")
            
            async with GelonghuiScraper() as scraper:
                results = await scraper.scrape()
                logger.info(f"Scraping completed: {len(results)} items")
                
                # Save to database (simplified for background task)
                # In production, you'd want more robust error handling
                
        except Exception as e:
            logger.error(f"Error in scraping task: {e}")
            
        # Wait 10 minutes before next scrape
        await asyncio.sleep(600)

async def run_analyzer():
    """Background task to run analysis periodically"""
    while True:
        try:
            logger.info("Starting scheduled analysis...")
            
            # Create a new database session for this task
            db = next(get_db())
            
            try:
                analyzer = HashtagAnalyzer(db)
                
                # Run analysis
                hashtag_analysis = await analyzer.analyze_hashtag_frequency()
                trending_topics = await analyzer.detect_trending_topics()
                
                # Save results
                await analyzer.save_trending_topics(trending_topics)
                
                logger.info(f"Analysis completed: {len(hashtag_analysis)} hashtags, {len(trending_topics)} trends")
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error in analysis task: {e}")
            
        # Wait 5 minutes before next analysis
        await asyncio.sleep(300)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )