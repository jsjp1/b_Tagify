from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class Article(BaseModel):
    id: int
    user_id: int
    title: str = ""
    body: Optional[str] = None
    encoded_content: str
    up_count: int = 0
    down_count: int = 0

    created_at: datetime
    updated_at: datetime


class AllArticlesLimitResponse(BaseModel):
    articles: List[Article]

    model_config = {"from_attributes": True}


class ArticleCreate(BaseModel):
    user_id: int
    title: str = ""
    body: Optional[str] = None
    encoded_content: str

    model_config = {"from_attributes": True}


class ArticleCreateResponse(BaseModel):
    id: int

    model_config = {"from_attributes": True}

    model_config = {"from_attributes": True}

    model_config = {"from_attributes": True}

    model_config = {"from_attributes": True}

    model_config = {"from_attributes": True}

    model_config = {"from_attributes": True}

    model_config = {"from_attributes": True}

    model_config = {"from_attributes": True}

    model_config = {"from_attributes": True}

    model_config = {"from_attributes": True}
