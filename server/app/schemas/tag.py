from typing import List, Literal, Optional

from app.schemas.common import Content
from pydantic import BaseModel, Field


class UserTags(BaseModel):
    user_id: int

    model_config = {"from_attributes": True}


class UserTagsResponse(BaseModel):
    tag: str
    tag_id: int
    color: int

    model_config = {"from_attributes": True}


class TagContents(BaseModel):
    tag_id: int

    model_config = {"from_attributes": True}


class TagContentsResponse(Content):
    id: int
    type: str

    model_config = {"from_attributes": True}


class TagPost(BaseModel):
    tagname: str

    model_config = {"from_attributes": True}


class TagPostResponse(BaseModel):
    id: int

    model_config = {"from_attributes": True}


class TagPut(BaseModel):
    tagname: str
    color: int

    model_config = {"from_attributes": True}


class TagPutResponse(BaseModel):
    id: int

    model_config = {"from_attributes": True}


class TagDelete(BaseModel):
    tagname: str

    model_config = {"from_attributes": True}


class TagDeleteResponse(BaseModel):
    id: int

    model_config = {"from_attributes": True}
