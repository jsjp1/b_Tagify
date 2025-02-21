from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class Content(BaseModel):
    id: int
    url: str
    title: str
    thumbnail: Optional[str]
    description: Optional[str]
    bookmark: bool
    video_length: Optional[int] = Field(default=0)
    body: Optional[str] = Field(default="")
    tags: List[str]

    model_config = {"from_attributes": True}


class ContentAnalyze(BaseModel):
    user_id: int
    url: str
    lang: Literal["en", "ko"] = Field(default="en")  # TODO: 추후 추가
    tag_count: Optional[int] = Field(default=3, ge=1, lt=10)
    detail_degree: Literal[1, 2, 3, 4, 5] = Field(default=3)

    model_config = {"from_attributes": True}


class ContentAnalyzeResponse(BaseModel):
    content_id: int

    model_config = {"from_attributes": True}


class UserContents(BaseModel):
    id: int

    model_config = {"from_attributes": True}


class UserContentsResponse(Content):
    pass
    

class UserBookmark(BaseModel):
    id: int
    
    model_config = {"from_attributes": True}
    
    
class UserBookmarkResponse(Content):
    pass