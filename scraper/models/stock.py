"""
Stock Model

Represents stock information related to news items.
"""

from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from .base import Base, BaseModel


class Stock(Base, BaseModel):
    """Stock model"""
    
    __tablename__ = 'stocks'
    
    # Foreign key to news item
    news_item_id = Column(Integer, ForeignKey('news_items.id', ondelete='CASCADE'), nullable=False)
    
    # Stock information
    market = Column(String(10))  # SH, SZ, HK, US, etc.
    code = Column(String(20), nullable=False)  # Stock code
    name = Column(String(100))  # Stock name
    can_click = Column(Boolean, default=False)  # Whether the stock is clickable in the original content
    full_name = Column(String(200))  # Full stock name
    exchange = Column(String(10))  # Exchange code (SH, SZ, HK, etc.)
    
    # Relationships
    news_item = relationship("NewsItem", back_populates="stocks")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'news_item_id': self.news_item_id,
            'market': self.market,
            'code': self.code,
            'name': self.name,
            'can_click': self.can_click,
            'full_name': self.full_name,
            'exchange': self.exchange,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f"<Stock(id={self.id}, code={self.code}, name='{self.name}', market={self.market})>"