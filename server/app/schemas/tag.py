from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class UserTags(BaseModel):
  oauth_id: str
  
  model_config = {"from_attributes": True}
    
class UserTagsResponse(BaseModel):
  tags: str
  tag_ids: int
  
  model_config = {"from_attributes": True}