from app.models.base import Base
from sqlalchemy import BIGINT, Column, ForeignKey, Text


class PostMetadata(Base):
    __tablename__ = "post_metadata"

    id = Column(BIGINT, primary_key=True)
    body = Column(Text, nullable=False)
    content_id = Column(
        BIGINT,
        ForeignKey("contents.id", ondelete="CASCADE"),
        nullable=False,
    )
