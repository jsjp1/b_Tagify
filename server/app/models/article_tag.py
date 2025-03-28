from app.models.base import Base
from sqlalchemy import BIGINT, Column, ForeignKey, Table
from sqlalchemy.orm import relationship

article_tag_association = Table(
    "article_tag",
    Base.metadata,
    Column(
        "article_id",
        BIGINT,
        ForeignKey("articles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id", BIGINT, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    ),
)
