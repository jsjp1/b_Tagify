from typing import List

from app.db import get_db
from app.schemas.tag import (
    TagContents,
    TagContentsResponse,
    TagDelete,
    TagDeleteResponse,
    TagPost,
    TagPostResponse,
    TagPut,
    TagPutResponse,
    UserTags,
    UserTagsResponse,
)
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
    request = UserTags(user_id=user_id)
    tags = await TagService.get_user_tags(request, db)

    return [
        UserTagsResponse(
            id=tag.id,
            tagname=tag.tagname,
            color=tag.color,
        )
        for tag in tags
    ]


@router.post("/user/{user_id}/create")
async def create(
    user_id: int,
    request: TagPost,
    db: Session = Depends(get_db),
) -> TagPostResponse:
    tag = await TagService.post_tag(user_id, request, db)
    return TagPostResponse(id=tag.id, tagname=tag.tagname, color=tag.color)


@router.put("/user/{user_id}/{tag_id}/update")
async def update_tag(
    user_id: int,
    tag_id: int,
    request: TagPut,
    db: Session = Depends(get_db),
) -> TagPutResponse:
    tag_id = await TagService.update_tag(user_id, tag_id, request, db)
    return TagPutResponse.model_validate({"id": tag_id}, from_attributes=True)


@router.delete("/user/{user_id}/delete")
async def delete(
    user_id: int,
    request: TagDelete,
    db: Session = Depends(get_db),
) -> TagDeleteResponse:
    tag_id = await TagService.delete_tag(user_id, request, db)
    return TagDeleteResponse.model_validate({"id": tag_id}, from_attributes=True)


@router.get("/{tag_id}/contents/all")
async def contents(
    tag_id: int,
    db: Session = Depends(get_db),
) -> List[TagContentsResponse]:
    request = TagContents(tag_id=tag_id)
    contents = await TagService.get_tag_all_contents(request, db)

    return [
        TagContentsResponse(
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
            type="video" if getattr(content, "video_metadata", None) else "post",
        )
        for content in contents
    ]


@router.get("/{tag_id}/contents/sub")
async def contents(
    tag_id: int,
    content_type: str,
    db: Session = Depends(get_db),
) -> List[TagContentsResponse]:
    request = TagContents(tag_id=tag_id)
    if content_type == "video":
        contents = await TagService.get_tag_videos(request, db)
    elif content_type == "post":
        contents = await TagService.get_tag_posts(request, db)
    else:
        raise HTTPException(status_code=400, detail="Invalid content type")

    return [
        TagContentsResponse(
            id=content.id,
            url=content.url,
            title=content.title,
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
            type="video" if getattr(content, "video_metadata", None) else "post",
        )
        for content in contents
    ]
