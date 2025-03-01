from typing import List

from app.db import get_db
from app.schemas.article import ArticleCreate, ArticleCreateResponse
from app.services.article import ArticleService
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("/endpoint_test")
def endpoint_test():
    return {"message": "ok"}


@router.post("/")
async def create_article(
    request: ArticleCreate, db: Session = Depends(get_db)
) -> ArticleCreateResponse:
    try:
        article_id = await ArticleService.post_article(request, db)
        return ArticleCreateResponse(id=article_id)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
