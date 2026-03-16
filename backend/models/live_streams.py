from sqlalchemy import Column, String, Integer, TIMESTAMP, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base, TimestampMixin

class LiveStream(Base, TimestampMixin):
    """Live stream metadata model"""
    __tablename__ = 'live_streams'
    
    stream_id = Column(String(100), primary_key=True, comment='Stream unique identifier')
    title = Column(String(500), nullable=False, comment='Stream title')
    start_time = Column(TIMESTAMP, nullable=True, comment='Stream start time')
    end_time = Column(TIMESTAMP, nullable=True, comment='Stream end time')
    status = Column(String(50), nullable=True, comment='Stream status (live, ended, scheduled)')
    viewer_count = Column(Integer, default=0, comment='Current viewer count')
    platform_source = Column(String(100), nullable=True, comment='Source platform')
    stream_url = Column(Text, nullable=True, comment='Stream URL')
    thumbnail_url = Column(Text, nullable=True, comment='Thumbnail image URL')
    description = Column(Text, nullable=True, comment='Stream description')
    channel_id = Column(String(100), nullable=True, comment='Channel identifier')
    channel_name = Column(String(200), nullable=True, comment='Channel name')
    is_premium = Column(Boolean, default=False, comment='Whether stream requires premium access')
    
    def __repr__(self):
        return f"<LiveStream(id={self.stream_id}, title='{self.title}', status='{self.status}')>"