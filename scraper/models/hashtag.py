"""
Hashtag Model

Represents hashtags extracted from news content.
"""

from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from .base import Base, BaseModel


class Hashtag(Base, BaseModel):
    """Hashtag model"""
    
    __tablename__ = 'hashtags'
    
    # Foreign key to news item
    news_item_id = Column(Integer, ForeignKey('news_items.id', ondelete='CASCADE'), nullable=False)
    
    # Hashtag information
    hashtag_text = Column(String(100), nullable=False)
    frequency = Column(Integer, default=1)  # How many times this hashtag appears in the content
    
    # Unique constraint to prevent duplicate hashtags for the same news item
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )
    
    # Relationships
    news_item = relationship("NewsItem", back_populates="hashtags")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'news_item_id': self.news_item_id,
            'hashtag_text': self.hashtag_text,
            'frequency': self.frequency,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f"<Hashtag(id={self.id}, text='{self.hashtag_text}', frequency={self.frequency})>"