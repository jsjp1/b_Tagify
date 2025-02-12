from app.models.base import Base
from sqlalchemy import BIGINT, Column, ForeignKey, Table
from sqlalchemy.orm import relationship

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
)
