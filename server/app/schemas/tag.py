from typing import List, Literal, Optional

from app.schemas.common import Content
from pydantic import BaseModel, Field


class UserTags(BaseModel):
    user_id: int


class UserTagsResponse(BaseModel):
    id: int
    tagname: str
    color: int

    model_config = {"from_attributes": True}


class TagContents(BaseModel):
    tag_id: int


class TagContentsResponse(Content):
    id: int
    type: str

    model_config = {"from_attributes": True}


class TagPost(BaseModel):
    tagname: str


class TagPostResponse(BaseModel):
    id: int

    model_config = {"from_attributes": True}


class TagPut(BaseModel):
    tagname: str
    color: int


class TagPutResponse(BaseModel):
    id: int

    model_config = {"from_attributes": True}


class TagDelete(BaseModel):
    tagname: str


class TagDeleteResponse(BaseModel):
    id: int

    model_config = {"from_attributes": True}
