from datetime import datetime, timezone
from sqlalchemy import Column, String, BIGINT, DateTime
from sqlalchemy.orm import relationship
from models.base import Base

class User(Base): 
  __tablename__ = "users"
  
  id = Column(BIGINT, primary_key=True, index=True)
  username = Column(String, unique=True, index=True)
  oauth_provider = Column(String)
  oauth_id = Column(String, unique=True)
  email = Column(String, unique=True, nullable=True)
  profile_image = Column(String, nullable=True)
  
  created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
  updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False)
  
  user_tags = relationship("UserTag", back_populates="user", cascade="all, delete-orphan")