from pydantic import BaseModel, EmailStr, AnyHttpUrl
from typing import Optional

class UserLogin(BaseModel):
    oauth_id: str
    email: Optional[EmailStr] = None
    
    model_config = {"from_attributes": True}

class UserCreate(BaseModel):
    username: str
    oauth_provider: str
    oauth_id: str
    email: Optional[EmailStr] = None
    profile_image: Optional[AnyHttpUrl] = None
    
    model_config = {"from_attributes": True}