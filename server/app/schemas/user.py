from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    username: str
    oauth_provider: str
    oauth_id: str
    email: Optional[EmailStr] = None
    profile_image: Optional[str] = None

    model_config = {"from_attributes": True}


class UserLogin(User):
    id_token: str


class UserWithTokens(User):
    id: int
    access_token: str = Field(..., min_length=10, description="JWT access token")
    refresh_token: str = Field(..., min_length=10, description="JWT refresh token")
    token_type: str = "bearer"


class AllUsersResponse(BaseModel):
    users: List[User]

    model_config = {"from_attributes": True}


class TokenRefresh(BaseModel):
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    access_token: str

    model_config = {"from_attributes": True}


class UserUpdateName(BaseModel):
    username: str


class UserUpdateNameResponse(BaseModel):
    id: int

    model_config = {"from_attributes": True}


class UserUpdateProfileImage(BaseModel):
    profile_image: str


class UserUpdateProfileImageResponse(BaseModel):
    id: int

    model_config = {"from_attributes": True}
