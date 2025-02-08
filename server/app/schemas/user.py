from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class UserLogin(BaseModel):
    oauth_id: str
    email: Optional[EmailStr] = None
    
    model_config = {"from_attributes": True}
    
class UserLoginResponse(BaseModel):
    username: str
    oauth_provider: str
    oauth_id: str
    email: Optional[EmailStr] = None
    profile_image: Optional[str] = None
    
    access_token: str = Field(..., min_length=10, description="JWT access token")
    refresh_token: str = Field(..., min_length=10, description="JWT refresh token")
    token_type: str = "bearer"
    
    model_config = {"from_attributes": True}
    
class UserCreate(BaseModel):
    username: str
    oauth_provider: str
    oauth_id: str
    email: Optional[EmailStr] = None
    profile_image: Optional[str] = None
    
    model_config = {"from_attributes": True}
    
class UserCreateResponse(BaseModel):
    oauth_id: str
    email: Optional[EmailStr] = None
    
    model_config = {"from_attributes": True}
    
class UserVideos(BaseModel):
    oauth_id: str
    
    model_config = {"from_attributes": True}
    
class UserVideosResponse(BaseModel):
    title: str
    link: str
    thumbnail: Optional[str]
    summation: Optional[str]
    video_length: int
    tags: List[str]
    
    model_config = {"from_attributes": True}