from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class UserTags(BaseModel):
    oauth_id: str

    model_config = {"from_attributes": True}


class UserTagsResponse(BaseModel):
    tag: str
    tag_id: int

    model_config = {"from_attributes": True}


class TagContents(BaseModel):
    tag_id: int

    model_config = {"from_attributes": True}


class TagContentsResponse(BaseModel):
    url: str
    title: str
    thumbnail: Optional[str]
    video_length: Optional[int] = Field(default=0)
    body: Optional[str] = Field(default="")

    model_config = {"from_attributes": True}