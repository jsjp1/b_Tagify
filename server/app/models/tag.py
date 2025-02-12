from app.models.base import Base
from app.models.content_tag import content_tag_association
from app.models.user_tag import user_tag_association
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    tagname = Column(String, unique=True, nullable=False, index=True)

    users = relationship("User", secondary=user_tag_association, back_populates="tags")
    contents = relationship(
        "Content", secondary=content_tag_association, back_populates="tags"
    )
