from pydantic import BaseModel, EmailStr
from typing import Optional

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