from app.router import content, tag, user
from fastapi import APIRouter

router = APIRouter(prefix="/api")
router.include_router(router=user.router)
router.include_router(router=content.router)
router.include_router(router=tag.router)
