from typing import List, Optional

from pydantic import BaseModel, Field


class ArticleCreate(BaseModel):
    user_id: int
    title: str = Field(default="")
    body: Optional[str] = Field(default="")
    encoded_content: str
    
    model_config = {"from_attributes": True}


class ArticleCreateResponse(BaseModel):
    id: int

    model_config = {"from_attributes": True}
