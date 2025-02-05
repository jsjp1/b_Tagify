from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config import get_settings
from db import get_db
from schemas.user import UserCreate, UserLogin
from services.user import UserService
from util.auth import create_access_token, create_refresh_token

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/endpoint_test")
def endpoint_test():
  return {"message": "ok"}

@router.post("/login")
async def login(
  request: UserLogin,
  db: Session = Depends(get_db),
  settings = Depends(get_settings),
):
  try:
    db_user = await UserService.get_user(request, db)
    
    access_token = create_access_token(
        settings,
        data={"sub": db_user.email}
    )
    refresh_token = create_refresh_token(
        settings,
        data={"sub": db_user.email + "refresh"}
    )
    
    return {"message": "success", "token_type": "Bearer", "access_token": access_token, "refresh_token": refresh_token, "existed_user_profile": db_user}

  except HTTPException as e:
    raise e
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/signup")
async def signup(
  request: UserCreate,
  db: Session = Depends(get_db),
):
  try: 
    new_user = await UserService.create_user(request, db)
    return {"message": "success", "created_user_profile": new_user}
  
  except HTTPException as e:
    raise e
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")