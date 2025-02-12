from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class UserTags(BaseModel):
    oauth_id: str

    model_config = {"from_attributes": True}


class UserTagsResponse(BaseModel):
    tag: str
    tag_id: int

    model_config = {"from_attributes": True}
