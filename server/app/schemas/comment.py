from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class CommentModel(BaseModel):
    id: int
    user_id: int
    user_name: str
    user_profile_image: Optional[str]
    body: str
    up_count: int
    down_count: int

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ArticleCommentsResponse(BaseModel):
    comments: List[CommentModel]

    model_config = {"from_attributes": True}

class PostCommentRequest(BaseModel):
    user_id: int
    body: str

class PostCommentResponse(BaseModel):
    id: int

    model_config = {"from_attributes": True}