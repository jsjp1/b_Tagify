from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class UserTags(BaseModel):
    user_id: int

    model_config = {"from_attributes": True}


class UserTagsResponse(BaseModel):
    tag: str
    tag_id: int

    model_config = {"from_attributes": True}


class TagContents(BaseModel):
    tag_id: int

    model_config = {"from_attributes": True}


class TagContentsResponse(BaseModel):
    id: int
    url: str
    title: str
    thumbnail: Optional[str]
    video_length: Optional[int] = Field(default=0)
    body: Optional[str] = Field(default="")

    model_config = {"from_attributes": True}


class TagPost(BaseModel):
    tagname: str

    model_config = {"from_attributes": True}


class TagPostResponse(BaseModel):
    id: int

    model_config = {"from_attributes": True}


class TagDelete(BaseModel):
    tagname: str

    model_config = {"from_attributes": True}


class TagDeleteResponse(BaseModel):
    id: int

    model_config = {"from_attributes": True}