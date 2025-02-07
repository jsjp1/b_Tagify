from fastapi import APIRouter
from app.router import user, video

router = APIRouter(prefix="/api")
router.include_router(router=user.router)
router.include_router(router=video.router)