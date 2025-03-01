from datetime import datetime, timezone

from app.models.base import Base
from sqlalchemy import BIGINT, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship


class Comment(Base):
    __tablename__ = "comments"

    id = Column(BIGINT, primary_key=True, index=True)
    body = Column(String, nullable=False, default="")
    up_count = Column(Integer, default=0)
    down_count = Column(Integer, default=0)

    user_id = Column(BIGINT, ForeignKey("users.id", ondelete="CASCADE"))
    article_id = Column(BIGINT, ForeignKey("articles.id", ondelete="CASCADE"))

    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User", back_populates="contents")
