from typing import List

from app.db import get_db
from app.schemas.common import (
    ContentModel,
    ContentResponseModel,
    DefaultSuccessResponse,
)
from app.schemas.content import (
    ContentAnalyze,
    ContentAnalyzeResponse,
    ContentPost,
    ContentPostResponse,
    ContentPutRequest,
    ContentPutResponse,
    SearchContentResponse,
    TagResponse,
    UserBookmark,
    UserBookmarkResponse,
    UserContents,
    UserContentsResponse,
)
from app.services.content import ContentService
from app.services.post import PostService
from app.services.video import VideoService
from config import get_settings
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/contents", tags=["contents"])


@router.get("/endpoint_test")
def endpoint_test():
    return {"message": "ok"}


@router.post("/analyze")
async def analyze(
    content_type: str,
    request: ContentAnalyze,
    db: AsyncSession = Depends(get_db),
    settings=Depends(get_settings),
) -> ContentAnalyzeResponse:
    if content_type == "video":
        return await VideoService.analyze_video(request, db, settings)
    elif content_type == "post":
        return await PostService.analyze_post(request, db)
    raise HTTPException(status_code=400, detail="Invalid content type")


@router.post("/save")
async def save(
    content_type: str,
    request: ContentPost,
    db: AsyncSession = Depends(get_db),
) -> ContentPostResponse:
    content_data = await ContentService.post_content(
        content_type, request, db, commit=True
    )
    tag_responses = [
        TagResponse(
            id=tag.id,
            tagname=tag.tagname,
            color=tag.color,
        )
        for tag in content_data["tags"]
    ]
    return ContentPostResponse(id=content_data["id"], tags=tag_responses)


@router.delete("/{content_id}")
async def delete(
    content_id: int,
    db: AsyncSession = Depends(get_db),
) -> DefaultSuccessResponse:
    await ContentService.delete_content(content_id, db)
    return DefaultSuccessResponse(message="success").model_dump()


@router.get("/user/{user_id}/all")
async def contents(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> List[UserContentsResponse]:
    request = UserContents(id=user_id)
    contents = await ContentService.get_user_all_contents(request, db)
    return [
        UserContentsResponse(
            id=content.id,
            title=content.title,
            url=content.url,
            thumbnail=content.thumbnail,
            favicon=content.favicon,
            description=content.description,
            bookmark=content.bookmark,
            **(
                {"video_length": content.video_metadata.video_length}
                if getattr(content, "video_metadata", None)
                else {}
            ),
            **(
                {"body": content.post_metadata.body}
                if getattr(content, "post_metadata", None)
                else {}
            ),
            tags=([tag.tagname for tag in content.tags] if content.tags else []),
            created_at=content.created_at,
            type="video" if getattr(content, "video_metadata", None) else "post",
        )
        for content in contents
    ]


@router.get("/user/{user_id}/sub")
async def contents(
    user_id: int,
    content_type: str,
    db: AsyncSession = Depends(get_db),
) -> List[UserContentsResponse]:
    request = UserContents(id=user_id)
    contents = await ContentService.get_user_all_sub_contents(request, content_type, db)
    return [
        UserContentsResponse(
            id=content.id,
            title=content.title,
            url=content.url,
            thumbnail=content.thumbnail,
            favicon=content.favicon,
            description=content.description,
            bookmark=content.bookmark,
            **(
                {"video_length": content.video_metadata.video_length}
                if content_type == "video"
                else {}
            ),
            **({"body": content.post_metadata.body} if content_type == "post" else {}),
            tags=([tag.tagname for tag in content.tags] if content.tags else []),
            created_at=content.created_at,
            type="video" if getattr(content, "video_metadata", None) else "post",
        )
        for content in contents
    ]


@router.get("/bookmarks/user/{user_id}")
async def bookmark(
    user_id: int, db: AsyncSession = Depends(get_db)
) -> List[UserBookmarkResponse]:
    request = UserBookmark(user_id=user_id)
    contents = await ContentService.get_bookmarked_contents(request, db)
    return [
        UserBookmarkResponse(
            id=content.id,
            title=content.title,
            url=content.url,
            thumbnail=content.thumbnail,
            favicon=content.favicon,
            description=content.description,
            bookmark=content.bookmark,
            **(
                {"video_length": content.video_metadata.video_length}
                if getattr(content, "video_metadata", None)
                else {}
            ),
            **(
                {"body": content.post_metadata.body}
                if getattr(content, "post_metadata", None)
                else {}
            ),
            tags=([tag.tagname for tag in content.tags] if content.tags else []),
            created_at=content.created_at,
            type="video" if getattr(content, "video_metadata", None) else "post",
        )
        for content in contents
    ]


@router.post("/{content_id}/bookmark")
async def bookmark(content_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    await ContentService.toggle_bookmark(content_id, db)
    return DefaultSuccessResponse(message="success").model_dump()


@router.put("/{content_id}/user/{user_id}")
async def edit(
    user_id: int,
    content_id: int,
    request: ContentPutRequest,
    db: AsyncSession = Depends(get_db),
) -> ContentPutResponse:
    tags = await ContentService.put_content(user_id, content_id, request, db)
    return ContentPutResponse(tags=tags)


@router.get("/user/{user_id}/search/{keyword}")
async def search(
    user_id: int, keyword: str, db: AsyncSession = Depends(get_db)
) -> SearchContentResponse:
    contents = await ContentService.get_search_contents(user_id, keyword, db)
    return SearchContentResponse(
        contents=[
            ContentResponseModel(
                id=content.id,
                url=content.url,
                title=content.title,
                thumbnail=content.thumbnail,
                favicon=content.favicon,
                description=content.description,
                bookmark=content.bookmark,
                **(
                    {"video_length": content.video_metadata.video_length}
                    if getattr(content, "video_metadata", None)
                    else {}
                ),
                **(
                    {"body": content.post_metadata.body}
                    if getattr(content, "post_metadata", None)
                    else {}
                ),
                tags=([tag.tagname for tag in content.tags] if content.tags else []),
                created_at=content.created_at,
            )
            for content in contents
        ]
    )
