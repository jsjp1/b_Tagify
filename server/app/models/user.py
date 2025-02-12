from datetime import datetime, timezone

from app.models.base import Base
from app.models.user_tag import user_tag_association
from sqlalchemy import BIGINT, Column, DateTime, String
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(BIGINT, primary_key=True, index=True)
    username = Column(String, index=True, nullable=False)
    oauth_provider = Column(String, nullable=False)
    oauth_id = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=True)
    profile_image = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        nullable=False,
    )

    contents = relationship(
        "Content",
        back_populates="user",
    )
    tags = relationship(
        "Tag",
        secondary=user_tag_association,
        back_populates="users",
    )
