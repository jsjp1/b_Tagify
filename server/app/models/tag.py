from app.models.article_tag import article_tag_association
from app.models.base import Base
from app.models.content_tag import content_tag_association
from sqlalchemy import BIGINT, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship


class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = (UniqueConstraint("user_id", "tagname", name="uq_user_tagname"),)

    id = Column(Integer, primary_key=True, index=True)
    tagname = Column(String, nullable=False, index=True)
    color = Column(BIGINT, nullable=True, default=4288585374)  # default = Colors.grey

    user_id = Column(BIGINT, ForeignKey("users.id", ondelete="CASCADE"))

    contents = relationship(
        "Content",
        secondary=content_tag_association,
        back_populates="tags",
        lazy="noload",
    )
    articles = relationship(
        "Article",
        secondary=article_tag_association,
        back_populates="tags",
        lazy="noload",
    )
