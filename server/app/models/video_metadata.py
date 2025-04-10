from app.models.base import Base
from sqlalchemy import BIGINT, Column, ForeignKey
from sqlalchemy.orm import relationship


class VideoMetadata(Base):
    __tablename__ = "video_metadata"

    id = Column(BIGINT, primary_key=True, index=True)
    video_length = Column(BIGINT, nullable=False)
    content_id = Column(
        BIGINT, ForeignKey("contents.id", ondelete="CASCADE"), nullable=False
    )

    content = relationship(
        "Content",
        back_populates="video_metadata",
        lazy="joined",
    )
