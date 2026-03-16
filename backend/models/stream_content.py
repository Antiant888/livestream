from sqlalchemy import Column, Integer, String, TIMESTAMP, Text, DECIMAL
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import ForeignKey
from .base import Base, TimestampMixin

class StreamContent(Base, TimestampMixin):
    """Stream content and chat messages model"""
    __tablename__ = 'stream_content'
    
    content_id = Column(Integer, primary_key=True, autoincrement=True)
    stream_id = Column(String(100), ForeignKey('live_streams.stream_id'), nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False, comment='Content timestamp')
    content_type = Column(String(50), nullable=False, comment='Type: chat, comment, description, etc.')
    text_content = Column(Text, nullable=True, comment='Main content text')
    hashtags = Column(JSONB, nullable=True, comment='Extracted hashtags')
    mentions = Column(JSONB, nullable=True, comment='Extracted user mentions')
    sentiment_score = Column(DECIMAL(3,2), nullable=True, comment='Sentiment analysis score (-1 to 1)')
    user_id = Column(String(100), nullable=True, comment='User identifier for chat messages')
    username = Column(String(200), nullable=True, comment='Username for chat messages')
    message_type = Column(String(50), nullable=True, comment='Message type: text, emoji, image, etc.')
    
    def __repr__(self):
        return f"<StreamContent(id={self.content_id}, stream='{self.stream_id}', type='{self.content_type}')>"