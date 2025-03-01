from datetime import datetime, timezone

from app.models.base import Base
from sqlalchemy import BIGINT, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Article(Base):
    __tablename__ = "articles"

    id = Column(BIGINT, primary_key=True, index=True)
    title = Column(String, nullable=False, default="")
    body = Column(String, nullable=True, default="")
    encoded_content = Column(String, nullable=False)
    up_count = Column(Integer, default=0)
    down_count = Column(Integer, default=0)

    user_id = Column(BIGINT, ForeignKey("users.id", ondelete="CASCADE"))

    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User", back_populates="articles")
