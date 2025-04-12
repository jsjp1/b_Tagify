import enum
from datetime import datetime, timezone

from app.models.base import Base
from app.models.content_tag import content_tag_association
from sqlalchemy import BIGINT, Boolean, Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import relationship


class ContentTypeEnum(str, enum.Enum):
    VIDEO = "video"
    POST = "post"


class Content(Base):
    __tablename__ = "contents"

    id = Column(BIGINT, primary_key=True, index=True)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True, default="")
    bookmark = Column(Boolean, nullable=False, default=False)
    thumbnail = Column(String, nullable=True)
    favicon = Column(String, nullable=True)
    content_type = Column(Enum(ContentTypeEnum), nullable=False)

    user_id = Column(BIGINT, ForeignKey("users.id", ondelete="CASCADE"))

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

    tags = relationship(
        "Tag",
        order_by="asc(Tag.id)",
        secondary=content_tag_association,
        back_populates="contents",
        lazy="selectin",
        join_depth=1,
    )
    video_metadata = relationship(
        "VideoMetadata",
        uselist=False,
        lazy="selectin",
    )
    post_metadata = relationship(
        "PostMetadata",
        uselist=False,
        lazy="selectin",
    )
