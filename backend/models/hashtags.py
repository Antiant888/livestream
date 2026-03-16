from sqlalchemy import Column, Integer, String, TIMESTAMP, DECIMAL
from sqlalchemy import UniqueConstraint
from .base import Base, TimestampMixin

class Hashtag(Base, TimestampMixin):
    """Hashtag frequency and metadata model"""
    __tablename__ = 'hashtags'
    
    hashtag_id = Column(Integer, primary_key=True, autoincrement=True)
    hashtag_text = Column(String(200), nullable=False, unique=True, comment='Hashtag text without #')
    frequency = Column(Integer, default=0, nullable=False, comment='Total frequency count')
    first_seen = Column(TIMESTAMP, nullable=True, comment='First occurrence timestamp')
    last_seen = Column(TIMESTAMP, nullable=True, comment='Last occurrence timestamp')
    is_trending = Column(DECIMAL(3,2), default=0.0, comment='Trending score based on recent activity')
    
    __table_args__ = (
        UniqueConstraint('hashtag_text', name='uix_hashtag_text'),
    )
    
    def __repr__(self):
        return f"<Hashtag(id={self.hashtag_id}, text='{self.hashtag_text}', freq={self.frequency})>"

class TrendingTopic(Base, TimestampMixin):
    """Trending topics detection model"""
    __tablename__ = 'trending_topics'
    
    topic_id = Column(Integer, primary_key=True, autoincrement=True)
    topic_name = Column(String(500), nullable=False, comment='Topic name or hashtag')
    score = Column(DECIMAL(10,2), nullable=False, comment='Trending score')
    timestamp = Column(TIMESTAMP, nullable=False, comment='Detection timestamp')
    source_stream = Column(String(100), nullable=True, comment='Source stream ID')
    hashtag_count = Column(Integer, default=0, comment='Number of related hashtags')
    topic_type = Column(String(50), default='hashtag', comment='Type: hashtag, keyword, phrase')
    confidence = Column(DECIMAL(3,2), default=0.0, comment='Detection confidence score')
    
    def __repr__(self):
        return f"<TrendingTopic(id={self.topic_id}, name='{self.topic_name}', score={self.score})>"