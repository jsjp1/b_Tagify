from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
from models.base import Base


class VideoTag(Base):
  __tablename__ = "video_tags"
  
  id = Column(Integer, primary_key=True, index=True)
  video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
  tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
  created_at = Column(TIMESTAMP, server_default=func.now())
  
  video = relationship("Video", back_populates="video_tags", passive_deletes=True)
  tag = relationship("Tag", back_populates="user_tags", passive_deletes=True)