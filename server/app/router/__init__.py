from fastapi import APIRouter
from app.router import user

router = APIRouter(prefix="/api")
router.include_router(router=user.router)