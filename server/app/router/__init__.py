from fastapi import APIRouter
from app.router import user, video, tag

router = APIRouter(prefix="/api")
router.include_router(router=user.router)
router.include_router(router=video.router)
router.include_router(router=tag.router)