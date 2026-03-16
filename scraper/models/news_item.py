"""
News Item Model

Represents a single news item from the Gelonghui API.
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, BigInteger, Float
from sqlalchemy.orm import relationship
from .base import Base, BaseModel


class NewsItem(Base, BaseModel):
    """News item model"""
    
    __tablename__ = 'news_items'
    
    # API fields
    glonghui_id = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(Text)
    content = Column(Text, nullable=False)
    content_prefix = Column(String(100))
    create_timestamp = Column(BigInteger, nullable=False, index=True)
    update_timestamp = Column(BigInteger, index=True)
    level = Column(Integer, default=0)
    route = Column(String(500))
    close_comment = Column(Boolean, default=False)
    
    # Engagement metrics
    read_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    favorite_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    
    # Calculated fields
    engagement_score = Column(Float, default=0.0)
    
    # Scraping metadata
    scraped_at = Column(DateTime, default=None)
    
    # Relationships
    stocks = relationship("Stock", back_populates="news_item", cascade="all, delete-orphan")
    hashtags = relationship("Hashtag", back_populates="news_item", cascade="all, delete-orphan")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Calculate engagement score if not provided
        if 'engagement_score' not in kwargs:
            self.calculate_engagement_score()
    
    def calculate_engagement_score(self):
        """Calculate engagement score based on metrics"""
        self.engagement_score = (
            self.read_count * 0.1 +
            self.share_count * 2.0 +
            self.comment_count * 1.0 +
            self.like_count * 0.5
        )
    
    def to_dict(self):
        """Convert to dictionary with relationships"""
        data = super().to_dict()
        data['stocks'] = [stock.to_dict() for stock in self.stocks]
        data['hashtags'] = [hashtag.to_dict() for hashtag in self.hashtags]
        return data
    
    def __repr__(self):
        return f"<NewsItem(id={self.id}, glonghui_id={self.glonghui_id}, title='{self.title[:50]}...')>"