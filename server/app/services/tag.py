from typing import List
from sqlalchemy.orm import Session
from app.schemas.tag import UserTags
from app.models.tag import Tag
from app.models.user import User
from app.models.user_tag import UserTag

class TagService():
  @staticmethod
  async def get_user_tags(user: UserTags, db: Session) -> List[Tag]:
    tags = (
      db.query(Tag)
      .join(UserTag, UserTag.tag_id == Tag.id)
      .join(User, User.id == UserTag.user_id)
      .filter(User.oauth_id == user.oauth_id)
      .all()
    )
    
    return tags