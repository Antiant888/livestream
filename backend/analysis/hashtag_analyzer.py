import asyncio
import json
import logging
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
import jieba
from loguru import logger

from ..models.stream_content import StreamContent
from ..models.hashtags import Hashtag, TrendingTopic
from ..database.config import get_db

class HashtagAnalyzer:
    """Analyze hashtag frequency and trending topics"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.stop_words = self.load_stop_words()
        
    def load_stop_words(self) -> set:
        """Load common stop words to filter out"""
        return {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看',
            '好', '自己', '这', '那', '来', '他', '她', '们', '这个', '那个', '什么',
            '怎么', '为什么', '哪里', '多少', '几', '第', '每', '各', '每', '最',
            '非常', '特别', '真的', '其实', '就是', '还是', '已经', '正在', '将要',
            '可以', '能够', '应该', '必须', '需要', '想要', '希望', '觉得', '认为'
        }
        
    async def analyze_hashtag_frequency(self, 
                                      time_window: int = 24,  # hours
                                      limit: int = 100) -> List[Dict[str, Any]]:
        """Analyze hashtag frequency in the specified time window"""
        try:
            # Calculate time threshold
            time_threshold = datetime.utcnow() - timedelta(hours=time_window)
            
            # Query hashtags from stream content
            results = self.db.query(
                StreamContent.hashtags,
                StreamContent.timestamp
            ).filter(
                StreamContent.timestamp >= time_threshold,
                StreamContent.hashtags.isnot(None)
            ).all()
            
            # Aggregate hashtag frequencies
            hashtag_counts = defaultdict(int)
            hashtag_streams = defaultdict(set)
            hashtag_times = defaultdict(list)
            
            for content in results:
                hashtags = content.hashtags
                if hashtags:
                    for hashtag in hashtags:
                        clean_tag = self.clean_hashtag(hashtag)
                        if clean_tag and len(clean_tag) > 1:
                            hashtag_counts[clean_tag] += 1
                            hashtag_streams[clean_tag].add(content.timestamp.strftime('%Y-%m-%d %H:%M'))
                            hashtag_times[clean_tag].append(content.timestamp)
            
            # Convert to list and sort by frequency
            hashtag_list = []
            for hashtag, count in hashtag_counts.items():
                # Calculate additional metrics
                stream_count = len(hashtag_streams[hashtag])
                first_seen = min(hashtag_times[hashtag]) if hashtag_times[hashtag] else None
                last_seen = max(hashtag_times[hashtag]) if hashtag_times[hashtag] else None
                
                hashtag_list.append({
                    'hashtag': hashtag,
                    'frequency': count,
                    'stream_count': stream_count,
                    'first_seen': first_seen,
                    'last_seen': last_seen,
                    'velocity': self.calculate_velocity(hashtag_times[hashtag], time_window)
                })
            
            # Sort by frequency and limit results
            hashtag_list.sort(key=lambda x: x['frequency'], reverse=True)
            return hashtag_list[:limit]
            
        except Exception as e:
            logger.error(f"Error analyzing hashtag frequency: {e}")
            return []
            
    def clean_hashtag(self, hashtag: str) -> Optional[str]:
        """Clean and normalize hashtag"""
        if not hashtag:
            return None
            
        # Remove common prefixes/suffixes
        hashtag = hashtag.strip().lower()
        hashtag = hashtag.replace('#', '').replace('@', '')
        
        # Remove punctuation and special characters
        hashtag = ''.join(c for c in hashtag if c.isalnum() or c in '\u4e00-\u9fff')
        
        # Filter out stop words and very short hashtags
        if len(hashtag) < 2 or hashtag in self.stop_words:
            return None
            
        return hashtag
        
    def calculate_velocity(self, timestamps: List[datetime], time_window: int) -> float:
        """Calculate hashtag velocity (rate of appearance)"""
        if not timestamps:
            return 0.0
            
        if len(timestamps) < 2:
            return 1.0
            
        # Calculate time span
        time_span = max(timestamps) - min(timestamps)
        if time_span.total_seconds() == 0:
            return float(len(timestamps))
            
        # Calculate velocity as frequency per hour
        hours_span = time_span.total_seconds() / 3600
        velocity = len(timestamps) / hours_span
        
        return round(velocity, 2)
        
    async def detect_trending_topics(self, 
                                   time_window: int = 24,
                                   min_frequency: int = 5,
                                   min_velocity: float = 0.5) -> List[Dict[str, Any]]:
        """Detect trending topics based on frequency and velocity"""
        try:
            # Get hashtag analysis results
            hashtag_analysis = await self.analyze_hashtag_frequency(time_window)
            
            trending_topics = []
            
            for hashtag_data in hashtag_analysis:
                frequency = hashtag_data['frequency']
                velocity = hashtag_data['velocity']
                
                # Apply trending criteria
                if frequency >= min_frequency and velocity >= min_velocity:
                    # Calculate trending score
                    score = self.calculate_trending_score(frequency, velocity, hashtag_data)
                    
                    trending_topics.append({
                        'topic_name': hashtag_data['hashtag'],
                        'score': score,
                        'frequency': frequency,
                        'velocity': velocity,
                        'stream_count': hashtag_data['stream_count'],
                        'first_seen': hashtag_data['first_seen'],
                        'last_seen': hashtag_data['last_seen'],
                        'topic_type': 'hashtag',
                        'confidence': self.calculate_confidence(frequency, velocity)
                    })
            
            # Sort by score and return top trends
            trending_topics.sort(key=lambda x: x['score'], reverse=True)
            return trending_topics
            
        except Exception as e:
            logger.error(f"Error detecting trending topics: {e}")
            return []
            
    def calculate_trending_score(self, frequency: int, velocity: float, hashtag_data: Dict) -> float:
        """Calculate trending score based on multiple factors"""
        # Base score from frequency and velocity
        base_score = frequency * velocity
        
        # Boost for recent activity
        last_seen = hashtag_data.get('last_seen')
        if last_seen:
            time_diff = datetime.utcnow() - last_seen
            recency_factor = max(0, 1 - (time_diff.total_seconds() / 3600) / 24)  # Decay over 24 hours
            base_score *= (1 + recency_factor)
            
        # Boost for spread across streams
        stream_count = hashtag_data.get('stream_count', 1)
        spread_factor = min(stream_count / 10, 2.0)  # Max 2x boost for spread
        base_score *= (1 + spread_factor)
        
        return round(base_score, 2)
        
    def calculate_confidence(self, frequency: int, velocity: float) -> float:
        """Calculate confidence score for trend detection"""
        # Simple confidence calculation based on frequency and velocity
        confidence = min(1.0, (frequency * velocity) / 100)
        return round(confidence, 2)
        
    async def analyze_sentiment_trends(self, 
                                     time_window: int = 24,
                                     hashtag_filter: Optional[str] = None) -> Dict[str, Any]:
        """Analyze sentiment trends for hashtags"""
        try:
            time_threshold = datetime.utcnow() - timedelta(hours=time_window)
            
            # Build query
            query = self.db.query(
                StreamContent.hashtags,
                StreamContent.sentiment_score,
                StreamContent.timestamp
            ).filter(
                StreamContent.timestamp >= time_threshold,
                StreamContent.sentiment_score.isnot(None),
                StreamContent.hashtags.isnot(None)
            )
            
            if hashtag_filter:
                query = query.filter(
                    StreamContent.hashtags.contains([hashtag_filter])
                )
                
            results = query.all()
            
            # Analyze sentiment by hashtag
            hashtag_sentiments = defaultdict(list)
            
            for content in results:
                hashtags = content.hashtags
                sentiment = content.sentiment_score
                
                if hashtags and sentiment is not None:
                    for hashtag in hashtags:
                        clean_tag = self.clean_hashtag(hashtag)
                        if clean_tag:
                            hashtag_sentiments[clean_tag].append({
                                'sentiment': sentiment,
                                'timestamp': content.timestamp
                            })
            
            # Calculate sentiment metrics
            sentiment_analysis = {}
            for hashtag, sentiments in hashtag_sentiments.items():
                if len(sentiments) < 3:  # Minimum data points
                    continue
                    
                scores = [s['sentiment'] for s in sentiments]
                timestamps = [s['timestamp'] for s in sentiments]
                
                sentiment_analysis[hashtag] = {
                    'average_sentiment': round(sum(scores) / len(scores), 2),
                    'sentiment_volatility': self.calculate_volatility(scores),
                    'positive_count': sum(1 for s in scores if s > 0.1),
                    'negative_count': sum(1 for s in scores if s < -0.1),
                    'neutral_count': sum(1 for s in scores if -0.1 <= s <= 0.1),
                    'total_mentions': len(scores),
                    'sentiment_trend': self.calculate_sentiment_trend(sentiments)
                }
            
            return sentiment_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment trends: {e}")
            return {}
            
    def calculate_volatility(self, scores: List[float]) -> float:
        """Calculate sentiment volatility"""
        if len(scores) < 2:
            return 0.0
            
        mean = sum(scores) / len(scores)
        variance = sum((score - mean) ** 2 for score in scores) / len(scores)
        return round(variance ** 0.5, 2)
        
    def calculate_sentiment_trend(self, sentiments: List[Dict]) -> str:
        """Calculate sentiment trend direction"""
        if len(sentiments) < 3:
            return "stable"
            
        # Sort by timestamp
        sentiments.sort(key=lambda x: x['timestamp'])
        
        # Calculate recent vs earlier sentiment
        mid_point = len(sentiments) // 2
        earlier_sentiment = sum(s['sentiment'] for s in sentiments[:mid_point]) / mid_point
        recent_sentiment = sum(s['sentiment'] for s in sentiments[mid_point:]) / (len(sentiments) - mid_point)
        
        diff = recent_sentiment - earlier_sentiment
        
        if diff > 0.1:
            return "improving"
        elif diff < -0.1:
            return "declining"
        else:
            return "stable"
            
    async def get_hashtag_timeline(self, 
                                 hashtag: str, 
                                 time_window: int = 24,
                                 interval_hours: int = 1) -> List[Dict[str, Any]]:
        """Get hashtag frequency timeline"""
        try:
            time_threshold = datetime.utcnow() - timedelta(hours=time_window)
            
            # Query data in time intervals
            timeline_data = []
            current_time = time_threshold
            
            while current_time < datetime.utcnow():
                end_time = current_time + timedelta(hours=interval_hours)
                
                count = self.db.query(func.count(StreamContent.id)).filter(
                    StreamContent.timestamp >= current_time,
                    StreamContent.timestamp < end_time,
                    StreamContent.hashtags.contains([hashtag])
                ).scalar()
                
                timeline_data.append({
                    'timestamp': current_time,
                    'frequency': count,
                    'hour': current_time.strftime('%H:%M')
                })
                
                current_time = end_time
                
            return timeline_data
            
        except Exception as e:
            logger.error(f"Error getting hashtag timeline: {e}")
            return []
            
    async def save_trending_topics(self, trending_topics: List[Dict[str, Any]]) -> bool:
        """Save trending topics to database"""
        try:
            # Clear old trending topics (keep last 24 hours)
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            self.db.query(TrendingTopic).filter(
                TrendingTopic.timestamp < cutoff_time
            ).delete()
            
            # Insert new trending topics
            for topic_data in trending_topics:
                topic = TrendingTopic(
                    topic_name=topic_data['topic_name'],
                    score=topic_data['score'],
                    timestamp=datetime.utcnow(),
                    hashtag_count=topic_data.get('frequency', 0),
                    topic_type=topic_data.get('topic_type', 'hashtag'),
                    confidence=topic_data.get('confidence', 0.0)
                )
                self.db.add(topic)
                
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error saving trending topics: {e}")
            self.db.rollback()
            return False
            
    async def get_real_time_stats(self) -> Dict[str, Any]:
        """Get real-time statistics"""
        try:
            now = datetime.utcnow()
            last_hour = now - timedelta(hours=1)
            
            # Count recent activity
            recent_content = self.db.query(func.count(StreamContent.id)).filter(
                StreamContent.timestamp >= last_hour
            ).scalar()
            
            recent_hashtags = self.db.query(func.count(func.distinct(StreamContent.id))).filter(
                StreamContent.timestamp >= last_hour,
                StreamContent.hashtags.isnot(None)
            ).scalar()
            
            # Get current trending topics
            trending = self.db.query(TrendingTopic).filter(
                TrendingTopic.timestamp >= last_hour
            ).order_by(desc(TrendingTopic.score)).limit(10).all()
            
            return {
                'timestamp': now,
                'recent_content_count': recent_content,
                'recent_hashtag_count': recent_hashtags,
                'active_trends': len(trending),
                'top_trends': [
                    {
                        'name': t.topic_name,
                        'score': float(t.score),
                        'confidence': float(t.confidence)
                    } for t in trending
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting real-time stats: {e}")
            return {}