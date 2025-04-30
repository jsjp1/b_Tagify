from typing import List, Optional

from pydantic import BaseModel, Field


class DefaultSuccessResponse(BaseModel):
    message: str


class ContentModel(BaseModel):
    url: str
    title: str
    thumbnail: Optional[str]
    favicon: Optional[str]
    description: Optional[str]
    bookmark: bool
    video_length: Optional[int] = Field(default=0)
    body: Optional[str] = Field(default="")
    tags: List[str]
    created_at: str

    model_config = {"from_attributes": True}


class ContentResponseModel(BaseModel):
    id: int
    url: str
    title: str
    thumbnail: Optional[str]
    favicon: Optional[str]
    description: Optional[str]
    bookmark: bool
    video_length: Optional[int] = Field(default=0)
    body: Optional[str] = Field(default="")
    tags: List[str]
    created_at: str

    model_config = {"from_attributes": True}
