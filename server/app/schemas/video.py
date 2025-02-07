from typing import Literal, Optional
from pydantic import BaseModel, AnyHttpUrl, Field


class VideoAnalyze(BaseModel):
  link: AnyHttpUrl
  tag_count: Optional[int] = Field(default=3)
  detail_degree: Literal[1, 2, 3, 4, 5] = Field(default=3)
  
  model_config = {"from_attributes": True}