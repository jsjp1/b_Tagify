from typing import List

from app.db import get_db
from app.schemas.tag import UserTags, UserTagsResponse
from app.services.tag import TagService
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/endpoint_test")
def endpoint_test():
    return {"message": "ok"}


@router.get("/user")
async def tags(
    oauth_id: str,
    db: Session = Depends(get_db),
) -> List[UserTagsResponse]:
    try:
        request = UserTags(oauth_id=oauth_id)
        tags = await TagService.get_user_tags(request, db)

        return [
            UserTagsResponse(
                tag=tag.tagname,
                tag_id=tag.id,
            )
            for tag in tags
        ]

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
