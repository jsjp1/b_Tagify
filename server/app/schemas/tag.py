from app.schemas.common import ContentResponseModel
from pydantic import BaseModel


class UserTags(BaseModel):
    user_id: int


class UserTagsResponse(BaseModel):
    id: int
    tagname: str
    color: int

    model_config = {"from_attributes": True}


class TagContents(BaseModel):
    tag_id: int


class TagContentsResponse(ContentResponseModel):
    type: str

    model_config = {"from_attributes": True}


class TagPost(BaseModel):
    tagname: str


class TagPostResponse(BaseModel):
    id: int
    tagname: str
    color: int

    model_config = {"from_attributes": True}


class TagPut(BaseModel):
    tagname: str
    color: int


class TagPutResponse(BaseModel):
    id: int

    model_config = {"from_attributes": True}


class TagDelete(BaseModel):
    id: int


class TagDeleteResponse(BaseModel):
    id: int

    model_config = {"from_attributes": True}
