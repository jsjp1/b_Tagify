from datetime import datetime, timezone

from app.models.base import Base
from sqlalchemy import BIGINT, Boolean, Column, DateTime, String
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(BIGINT, primary_key=True, index=True)
    username = Column(String, index=True, nullable=False)
    oauth_provider = Column(String, nullable=False)
    oauth_id = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=True)
    profile_image = Column(String, nullable=True)
    is_premium = Column(Boolean, default=False, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    contents = relationship(
        "Content",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    tags = relationship(
        "Tag",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    articles = relationship(
        "Article",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    comments = relationship(
        "Comment",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
