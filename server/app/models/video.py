from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from sqlalchemy import Column, String, BIGINT, DateTime
from app.models.base import Base

class Video(Base):
  __tablename__ = "videos"
  
  id = Column(BIGINT, primary_key=True, index=True)
  url = Column(String, nullable=False)
  title = Column(String, nullable=False)
  thumbnail = Column(String, nullable=True)
  video_length = Column(String, nullable=False)
  
  created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
  updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False)
  
  video_tags = relationship("VideoTag", back_populates="video", cascade="all, delete-orphan")
  user_videos = relationship("UserVideo", back_populates="video", cascade="all, delete-orphan", overlaps="users")
  users = relationship("User", secondary="user_videos", back_populates="videos", overlaps="user_videos")