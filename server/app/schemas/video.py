from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class VideoAnalyze(BaseModel):
  oauth_id: str
  url: str
  lang: Literal["en", "ko"] = Field(default="en") # TODO: 추후 추가
  tag_count: Optional[int] = Field(default=3, ge=1, lt=10)
  detail_degree: Literal[1, 2, 3, 4, 5] = Field(default=3)
  
  model_config = {"from_attributes": True}    
  
class VideoAnalyzeResponse(BaseModel):
  video_id: int
  
  model_config = {"from_attributes": True}
  
class UserVideos(BaseModel):
  oauth_id: str
  
  model_config = {"from_attributes": True}
    
class UserVideosResponse(BaseModel):
  url: str
  title: str
  thumbnail: Optional[str]
  summation: Optional[str]
  video_length: int
  tags: List[str]
  
  model_config = {"from_attributes": True}