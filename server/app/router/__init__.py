from app.router import article, comment, content, tag, user
from fastapi import APIRouter

router = APIRouter(prefix="/api")
router.include_router(router=user.router)
router.include_router(router=content.router)
router.include_router(router=tag.router)
router.include_router(router=article.router)
router.include_router(router=comment.router)