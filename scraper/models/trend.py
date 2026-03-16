"""
Trend Model

Represents calculated trends based on hashtag frequency and engagement.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.orm import relationship
from .base import Base, BaseModel
from datetime import datetime


class Trend(Base, BaseModel):
    """Trend model for hashtag popularity tracking"""
    
    __tablename__ = 'trends'
    
    # Trend information
    hashtag_text = Column(String(100), nullable=False, index=True)
    frequency = Column(Integer, default=0)  # Total frequency in the time window
    trend_score = Column(Float, default=0.0)  # Calculated trend score
    time_window = Column(String(20), default='1h')  # Time window: '1h', '24h', '7d'
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'hashtag_text': self.hashtag_text,
            'frequency': self.frequency,
            'trend_score': self.trend_score,
            'time_window': self.time_window,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f"<Trend(id={self.id}, hashtag='{self.hashtag_text}', score={self.trend_score}, window={self.time_window})>"