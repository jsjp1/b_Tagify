from typing import List

from pydantic import BaseModel


class Comment(BaseModel):
    id: int
    user_id: int
    body: str
    up_count: int
    down_count: int

    model_config = {"from_attributes": True}


class ArticleCommentsResponse(BaseModel):
    comments: List[Comment]

    model_config = {"from_attributes": True}
