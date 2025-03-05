from app.db import get_db
from app.schemas.user import (AllUsersResponse, TokenRefresh,
                              TokenRefreshResponse, User, UserLogin,
                              UserWithTokens)
from app.services.user import UserService
from app.util.auth import create_access_token, create_refresh_token
from config import get_settings
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/endpoint_test")
def endpoint_test():
    return {"message": "ok"}


@router.get("/")
async def users(
    db: Session = Depends(get_db),
) -> AllUsersResponse:
    try:
        db_users = await UserService.get_all_users(db)

        return AllUsersResponse(
            users=[User.model_validate(user, from_attributes=True) for user in db_users]
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/login")
async def login(
    request: UserLogin,
    db: Session = Depends(get_db),
    settings=Depends(get_settings),
) -> UserWithTokens:
    try:
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

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/token/refresh")
async def refresh(
    request: TokenRefresh,
    settings=Depends(get_settings),
) -> TokenRefreshResponse:
    try:
        new_access_token = await UserService.token_refresh(request, settings)
        return TokenRefreshResponse(access_token=new_access_token)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
