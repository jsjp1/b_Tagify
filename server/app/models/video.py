from models.base import Base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from sqlalchemy import Column, String, BIGINT, DateTime, ForeignKey

class Video(Base):
  __tablename__ = "videos"
  
  id = Column(BIGINT, primary_key=True, index=True)
  title = Column(String, nullable=False)
  thumbnail = Column(String, nullable=True)
  summation = Column(String, nullable=True)
  video_length = Column(String, nullable=False)
  
  user_id = Column(BIGINT, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
  
  created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
  updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False)
  
  video_tags = relationship("VideoTag", back_populates="video", cascade="all, delete-orphan")
  user = relationship("User", back_populates="videos") 