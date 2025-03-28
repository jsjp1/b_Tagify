from typing import List

from app.db import get_db
from app.schemas.article import (
    AllArticlesLimitResponse,
    ArticleCreate,
    ArticleCreateResponse,
    ArticleDelete,
    ArticleDeleteResponse,
    ArticleDownload,
    ArticleDownloadResponse,
    ArticleModel,
    ArticleTagResponse,
)
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
    article_id = await ArticleService.post_article(request, db)
    return ArticleCreateResponse(id=article_id)


@router.delete("/")
async def delete_article(
    request: ArticleDelete, db: Session = Depends(get_db)
) -> ArticleDeleteResponse:
    article_id = await ArticleService.delete_article(request, db)
    return ArticleDeleteResponse(id=article_id)


@router.get("/all")
async def get_all_articles_limit(
    limit: int,
    offset: int,
    db: Session = Depends(get_db),
) -> AllArticlesLimitResponse:
    articles = await ArticleService.get_all_articles_limit(limit, offset, db)
    return articles


@router.post("/download/{article_id}")
async def download_article(
    request: ArticleDownload,
    article_id: int,
    db: Session = Depends(get_db),
) -> ArticleDownloadResponse:
    tag_id = await ArticleService.download_article(request, article_id, db)
    return ArticleDownloadResponse(tag_id=tag_id)


@router.get("/tags/popular/{count}")
async def get_popular_tags(
    count: int,
    db: Session = Depends(get_db),
) -> ArticleTagResponse:
    popular_tags = await ArticleService.get_popular_tags(count, db)
    return ArticleTagResponse(tags=popular_tags)


@router.get("/tags/hot/{count}")
async def get_hot_tags(
    count: int,
    db: Session = Depends(get_db),
) -> ArticleTagResponse:
    hot_tags = await ArticleService.get_hot_tags(count, db)
    return ArticleTagResponse(tags=hot_tags)


@router.get("/tags/upvote/{count}")
async def get_upvote_tags(
    count: int,
    db: Session = Depends(get_db),
) -> ArticleTagResponse:
    upvote_tags = await ArticleService.get_upvote_tags(count, db)
    return ArticleTagResponse(tags=upvote_tags)


@router.get("/tags/newest/{count}")
async def get_newest_tags(
    count: int,
    db: Session = Depends(get_db),
) -> ArticleTagResponse:
    newest_tags = await ArticleService.get_newest_tags(count, db)
    return ArticleTagResponse(tags=newest_tags)


@router.get("/tags/owned/{user_id}/{count}")
async def get_owned_tags(
    user_id: int,
    count: int,
    db: Session = Depends(get_db),
) -> ArticleTagResponse:
    owned_tags = await ArticleService.get_owned_tags(user_id, count, db)
    return ArticleTagResponse(tags=owned_tags)
