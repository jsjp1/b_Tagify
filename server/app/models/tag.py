from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.base import Base

class Tag(Base):
  __tablename__ = "tags"
  
  id = Column(Integer, primary_key=True, index=True)
  tagname = Column(String, unique=True, nullable=False, index=True)
  
  user_tag = relationship("UserTag", back_populates="tag", cascade="all, delete-orphan")
  video_tag = relationship("VideoTag", back_populates="tag", cascade="all, delete-orphan")