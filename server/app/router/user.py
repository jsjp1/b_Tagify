from app.db import get_db
from app.schemas.user import (
    AllUsersResponse,
    CheckRefreshToken,
    RefreshTokenCheckResponse,
    TokenRefresh,
    TokenRefreshResponse,
    User,
    UserDelete,
    UserDeleteResponse,
    UserLogin,
    UserUpdateName,
    UserUpdateNameResponse,
    UserUpdatePremiumStateResponse,
    UserUpdateProfileImage,
    UserUpdateProfileImageResponse,
    UserWithTokens,
)
from app.services.user import UserService
from app.util.auth import create_access_token, create_refresh_token
from config import Settings, get_settings
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/endpoint_test")
def endpoint_test():
    return {"message": "ok"}


@router.get("/")
async def users(
    db: AsyncSession = Depends(get_db),
) -> AllUsersResponse:
    db_users = await UserService.get_all_users(db)

    return AllUsersResponse(
        users=[User.model_validate(user, from_attributes=True) for user in db_users]
    )


@router.post("/login")
async def login(
    request: UserLogin,
    db: AsyncSession = Depends(get_db),
    settings=Depends(get_settings),
) -> UserWithTokens:
    if request.oauth_provider in ("google", "Google"):
        db_user = await UserService.login_google(request, db, settings)
    elif request.oauth_provider in ("apple", "Apple"):
        db_user = await UserService.login_apple(request, db, settings)
    else:
        raise HTTPException(status_code=400, detail="Unsupported oauth provider")

    access_token = create_access_token(settings, data={"sub": db_user.email})
    refresh_token = create_refresh_token(settings, data={"sub": db_user.email})

    db_user.access_token = access_token
    db_user.refresh_token = refresh_token

    return UserWithTokens.model_validate(db_user, from_attributes=True)


@router.post("/me/delete")
async def delete(
    request: UserDelete,
    db: AsyncSession = Depends(get_db),
) -> UserDeleteResponse:
    deleted_user_id = await UserService.delete_user(request, db)
    return UserDeleteResponse(id=deleted_user_id)


@router.post("/token/refresh")
async def refresh(
    request: TokenRefresh,
    settings=Depends(get_settings),
) -> TokenRefreshResponse:
    new_tokens = await UserService.token_refresh(request, settings)
    return TokenRefreshResponse(tokens=new_tokens)


@router.put("/name/{user_id}")
async def update_name(
    request: UserUpdateName,
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> UserUpdateNameResponse:
    updated_user_id = await UserService.update_name(request, user_id, db)
    return UserUpdateNameResponse(id=updated_user_id)


@router.put("/profile_image/{user_id}")
async def update_name(
    request: UserUpdateProfileImage,
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> UserUpdateProfileImageResponse:
    updated_user_id = await UserService.update_profile_image(request, user_id, db)
    return UserUpdateProfileImageResponse(id=updated_user_id)


@router.put("/premium/{user_id}")
async def update_premium(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> UserUpdatePremiumStateResponse:
    updated_user_id = await UserService.update_premium_status(user_id, db)
    return UserUpdatePremiumStateResponse(id=updated_user_id)


@router.post("/token/check/refresh_token")
async def check_refresh_token(
    request: CheckRefreshToken,
    settings=Depends(get_settings),
) -> RefreshTokenCheckResponse:
    is_valid = await UserService.check_refresh_token(request, settings)
    return RefreshTokenCheckResponse(valid=is_valid)
