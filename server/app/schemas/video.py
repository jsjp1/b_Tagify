from typing import Literal, Optional
from pydantic import BaseModel, Field

class VideoAnalyze(BaseModel):
  link: str
  tag_count: Optional[int] = Field(default=3, ge=1, lt=10)
  detail_degree: Literal[1, 2, 3, 4, 5] = Field(default=3)
  
  model_config = {"from_attributes": True}    
  
class VideoAnalyzeResponse(BaseModel):
  video_id: int
  
  model_config = {"from_attributes": True}