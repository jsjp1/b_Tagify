from app.models.base import Base
from sqlalchemy import BIGINT, Column, ForeignKey, Index, Table

content_tag_association = Table(
    "content_tag",
    Base.metadata,
    Column(
        "content_id",
        BIGINT,
        ForeignKey("contents.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id", BIGINT, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    ),
    Index("idx_contenttag_content_id", "content_id"),
    Index("idx_content_tag_tag_id", "tag_id"),
)
