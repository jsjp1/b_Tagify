from typing import List

from app.db import get_db
from app.schemas.tag import TagContents, TagContentsResponse, UserTags, UserTagsResponse
from app.services.tag import TagService
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/endpoint_test")
def endpoint_test():
    return {"message": "ok"}


@router.get("/user/{user_id}")
async def tags(
    user_id: int,
    db: Session = Depends(get_db),
) -> List[UserTagsResponse]:
    try:
        request = UserTags(user_id=user_id)
        tags = await TagService.get_user_tags(request, db)

        return [
            UserTagsResponse(
                tag=tag.tagname,
                tag_id=tag.id,
            )
            for tag in tags
        ]

    except HTTPException as e:
        print(e)
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/{tag_id}/contents")
async def contents(
    tag_id: int,
    content_type: str,
    db: Session = Depends(get_db),
) -> List[TagContentsResponse]:
    try:
        request = TagContents(tag_id=tag_id)
        if content_type == "video":
            contents = await TagService.get_tag_videos(request, db)
        elif content_type == "post":
            pass
            # contents = await TagService.get_tag_posts(request, db)
        else:
            raise HTTPException(status_code=400, detail="Invalid content type")

        return [
            TagContentsResponse(
                id=content.id,
                url=content.url,
                title=content.title,
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
            )
            for content in contents
        ]

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
