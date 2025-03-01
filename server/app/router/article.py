from typing import List

from app.db import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("/endpoint_test")
def endpoint_test():
    return {"message": "ok"}

