from typing import List

from app.db import get_db
from app.schemas.content import (
    ContentAnalyze,
    ContentAnalyzeResponse,
    UserContents,
    UserContentsResponse,
)
from app.services.video import VideoService
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


@router.get("/user")
async def contents(
    oauth_id: str,
    content_type: str,
    db: Session = Depends(get_db),
) -> List[UserContentsResponse]:
    try:
        request = UserContents(oauth_id=oauth_id)
        if content_type == "video":
            contents = await VideoService.get_user_videos(request, db)
        elif content_type == "post":
            pass
            # contents = await PostService.get_user_posts(request, db)
        else:
            raise HTTPException(status_code=400, detail="Invalid content type")

        return [
            UserContentsResponse(
                title=content.title,
                url=content.url,
                thumbnail=content.thumbnail,
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
