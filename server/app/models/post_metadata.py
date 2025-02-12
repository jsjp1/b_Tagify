from app.models.base import Base
from sqlalchemy import BIGINT, Column, ForeignKey, Text
from sqlalchemy.orm import relationship


class PostMetadata(Base):
    __tablename__ = "post_metadata"

    id = Column(BIGINT, primary_key=True, index=True)
    body = Column(Text, nullable=False)
    content_id = Column(
        BIGINT,
        ForeignKey("contents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    content = relationship("Content", back_populates="post_metadata")
