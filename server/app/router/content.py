from typing import List

from app.db import get_db
from app.schemas.content import (
    ContentAnalyze,
    ContentAnalyzeResponse,
    UserContents,
    UserContentsResponse,
    UserBookmark,
    UserBookmarkResponse,
)
from app.services.video import VideoService
from app.services.content import ContentService
from config import get_settings
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/contents", tags=["contents"])


@router.get("/endpoint_test")
def endpoint_test():
    return {"message": "ok"}


@router.post("/analyze")
async def analyze(
    content_type: str,
    request: ContentAnalyze,
    db: Session = Depends(get_db),
    settings=Depends(get_settings),
) -> ContentAnalyzeResponse:
    try:
        if content_type == "video":
            content_id = await VideoService.analyze_video(
                content_type, request, db, settings
            )
        elif content_type == "post":
            pass
            # content_id = await PostService.analyze_post(request, db, settings)
        else:
            raise HTTPException(status_code=400, detail="Invalid content type")

        return content_id

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/user/all")
async def contents(
    oauth_id: str,
    db: Session = Depends(get_db),
) -> List[UserContentsResponse]:
    try:
        request = UserContents(oauth_id=oauth_id)
        contents = await ContentService.get_user_all_contents(request, db)

        return [
            UserContentsResponse(
                id=content.id
                title=content.title,
                url=content.url,
                thumbnail=content.thumbnail,
                description=content.description,
                **(
                    {"video_length": content.video_metadata.video_length}
                    if getattr(content, "video_metadata", None) else {}
                ),
                **(
                    {"body": content.post_metadata.body}
                    if getattr(content, "post_metadata", None) else {}
                ),
                tags=([tag.tagname for tag in content.tags] if content.tags else []),
            )
            for content in contents
        ]

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/user/sub")
async def contents(
    oauth_id: str,
    content_type: str,
    db: Session = Depends(get_db),
) -> List[UserContentsResponse]:
    try:
        request = UserContents(oauth_id=oauth_id)
        contents = await ContentService.get_user_all_sub_contents(request, content_type, db)

        return [
            UserContentsResponse(
                id=content.id,
                title=content.title,
                url=content.url,
                thumbnail=content.thumbnail,
                description=content.description,
                **(
                    {"video_length": content.video_metadata.video_length}
                    if content_type == "video"
                    else {}
                ),
                **(
                    {"body": content.post_metadata.body}
                    if content_type == "post"
                    else {}
                ),
                tags=([tag.tagname for tag in content.tags] if content.tags else []),
            )
            for content in contents
        ]

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/{content_id}/bookmark")
async def bookmark(
    content_id: str,
    request: UserBookmark,
    db: Session = Depends(get_db)
) -> dict:
    try:
        content_id = await ConentService.toggle_bookmark(request, content_id, db)
        return UserBookmarkResponse.model_validate(content_id, from_attributes=True)
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
