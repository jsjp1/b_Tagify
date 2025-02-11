from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey, String, func
from sqlalchemy.orm import relationship
from app.models.base import Base

class UserVideo(Base):
  __tablename__ = "user_videos"
  
  id = Column(Integer, primary_key=True, index=True)
  user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
  video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
  summation = Column(String, nullable=True)
  
  created_at = Column(TIMESTAMP, server_default=func.now())
  
  user = relationship("User", back_populates="user_videos")
  video = relationship("Video", back_populates="user_videos")