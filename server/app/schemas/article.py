from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ArticleModel(BaseModel):
    id: int
    user_id: int
    user_name: str
    user_profile_image: Optional[str]
    title: str = ""
    body: Optional[str] = None
    encoded_content: str
    up_count: int = 0
    down_count: int = 0

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AllArticlesLimitResponse(BaseModel):
    articles: List[ArticleModel]

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


class ArticleDelete(BaseModel):
    user_id: int
    article_id: int


class ArticleDeleteResponse(BaseModel):
    id: int

    model_config = {"from_attributes": True}


class ArticleDownload(BaseModel):
    user_id: int
    tag_name: str


class ArticleDownloadResponse(BaseModel):
    tag_id: int

    model_config = {"from_attributes": True}
