from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
from models.base import Base

class UserTag(Base):
  __tablename__ = "user_tags"
  
  id = Column(Integer, primary_key=True, index=True)
  user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
  tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
  created_at = Column(TIMESTAMP, server_default=func.now())
  
  user = relationship("User", back_populates="user_tags", passive_deletes=True)
  tag = relationship("Tag", back_populates="user_tags", passive_deletes=True)