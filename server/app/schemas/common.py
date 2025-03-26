from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DefaultSuccessResponse(BaseModel):
    message: str


class Content(BaseModel):
    url: str
    title: str
    thumbnail: Optional[str]
    favicon: Optional[str]
    description: Optional[str]
    bookmark: bool
    video_length: Optional[int] = Field(default=0)
    body: Optional[str] = Field(default="")
    tags: List[Dict[str, Any]]

    model_config = {"from_attributes": True}
