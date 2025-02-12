from app.models.base import Base
from sqlalchemy import Column, ForeignKey, Integer, Table
from sqlalchemy.orm import relationship

user_tag_association = Table(
    "user_tag",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)
