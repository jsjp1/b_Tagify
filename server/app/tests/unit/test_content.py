from unittest.mock import AsyncMock, patch

import pytest
from app.models.content import Content
from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.orm import joinedload, selectinload


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "field",
    [
        "url",
        "title",
        "thumbnail",
        "favicon",
        "description",
        "video_length",
        "body",
        "tags",
    ],
)
@pytest.mark.parametrize(
    ("content_type", "body"),
    [
        (
            "post",
            {
                "url": "https://www.github.com/",
                "lang": "en",
                "tag_count": 3,
                "detail_degree": 3,
            },
        ),
        (
            "video",
            {
                "url": "https://youtu.be/PCp2iXA1uLE?si=GvwmF0Wcoxe-mz7t",
                "lang": "en",
                "tag_count": 3,
                "detail_degree": 3,
            },
        ),
    ],
)
@patch("app.services.video.VideoService.analyze_video", new_callable=AsyncMock)
async def test_analyze_success(
    mock_analyze_video, auth_client, test_user_persist, content_type, body, field
):
    """
    콘텐츠 분석 성공 -> 200
    각 필드(url, title, thumbnail 등)가 응답에 포함되는지 확인
    """
    if content_type == "video":
        mock_analyze_video.return_value = {
            "url": body["url"],
            "title": "Mock Video",
            "thumbnail": "https://example.com/thumb.jpg",
            "favicon": "https://example.com/favicon.ico",
            "description": "Test description",
            "video_length": 300,
            "body": "mocked body",
            "tags": ["mock", "tag"],
        }

    body["user_id"] = test_user_persist.id

    response = await auth_client.post(
        f"/api/contents/analyze?content_type={content_type}", json=body
    )

    assert response.status_code == 200
    assert field in response.json()



@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("content_type", "body"),
    [
        (
            "post",
            {
                "url": "https://www.invalidurl.com/",
                "lang": "en",
                "tag_count": 3,
                "detail_degree": 3,
            },
        ),
    ],
)
async def test_analyze_success_with_invalid_url(
    auth_client, test_user_persist, content_type, body
):
    """
    존재하지 않는 post url analyze -> 200
    post의 경우, 실패 처리하지 않고 200 반환
    """
    body["user_id"] = test_user_persist.id

    response = await auth_client.post(
        f"/api/contents/analyze?content_type={content_type}", json=body
    )

    # 해당 video id의 video가 존재하지 않음
    assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("content_type", "body"),
    [
        (
            "video",
            {
                "url": "https://youtu.be/1234",
                "lang": "en",
                "tag_count": 3,
                "detail_degree": 3,
            },
        ),
    ],
)
@patch("app.services.video.VideoService.analyze_video", new_callable=AsyncMock)
async def test_analyze_fail_with_invalid_url(
    mock_analyze_video, auth_client, test_user_persist, content_type, body
):
    """
    존재하지 않는 url analyze -> 404 Unprocessable Entitiy
    """
    if content_type == "video":
        mock_analyze_video.side_effect = HTTPException(status_code=404, detail="Video not found on YouTube")

    body["user_id"] = test_user_persist.id

    response = await auth_client.post(
        f"/api/contents/analyze?content_type={content_type}", json=body
    )

    # 해당 video id의 video가 존재하지 않음
    assert response.status_code == 404
    assert response.json()["detail"] == "Video not found on YouTube"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("content_type", "body"),
    [
        (
            "post",
            {
                "url": "https://www.github.com/",
                "lang": "en",
                "tag_count": 3,
                "detail_degree": 3,
            },
        ),
    ],
)
async def test_analyze_fail_with_exists_content(
    auth_client, test_user_persist_with_content, content_type, body
):
    """
    이미 존재하는 contents를 analyze -> 400 Bad Request
    """
    body["user_id"] = test_user_persist_with_content.id

    response = await auth_client.post(
        f"/api/contents/analyze?content_type={content_type}", json=body
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Content already exists"


@pytest.mark.asyncio
@pytest.mark.parametrize("field", ["id", "tags"])
@pytest.mark.parametrize(
    ["content_type", "body"],
    [
        (
            "post",
            {
                "url": "https://www.github.com/",
                "title": "github",
                "thumbnail": "",
                "favicon": "",
                "description": "",
                "bookmark": False,
                "video_length": 0,
                "body": "",
                "tags": ["temp"],
            },
        )
    ],
)
async def test_save_content_success(
    auth_client, test_user_persist, db_session, content_type, body, field
):
    """
    새로운 콘텐츠를 저장할 때 200
    id, tags 필드가 포함되고 DB에 정상적으로 저장되는지 확인
    """
    body["user_id"] = test_user_persist.id

    # 저장 전엔 존재하지 않음을 확인
    async with db_session as session:
        result = await session.execute(
            select(Content).where(
                and_(
                    Content.user_id == test_user_persist.id, Content.url == body["url"]
                )
            )
        )
        db_content = result.scalar_one_or_none()
        assert db_content is None

    response = await auth_client.post(
        f"/api/contents/save?content_type={content_type}", json=body
    )

    response_json = response.json()

    # 저장 후에 존재함을 확인
    assert response.status_code == 200
    assert field in response_json
    async with db_session as session:
        result = await session.execute(
            select(Content).where(
                and_(
                    Content.user_id == test_user_persist.id, Content.url == body["url"]
                )
            )
        )
        db_content = result.scalar_one_or_none()
        assert db_content is not None
        assert db_content.user_id == test_user_persist.id


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["content_type", "body"],
    [
        (
            "post",
            {
                "url": "https://www.github.com/",
                "title": "github",
                "thumbnail": "",
                "favicon": "",
                "description": "",
                "bookmark": False,
                "video_length": 0,
                "body": "",
                "tags": ["temp"],
            },
        )
    ],
)
async def test_save_content_fail_with_invalid_user(auth_client, content_type, body):
    """
    존재하지 않는 사용자의 컨텐츠 저장 -> 404 Not found
    """
    body["user_id"] = 999999

    response = await auth_client.post(
        f"/api/contents/save?content_type={content_type}", json=body
    )

    assert response.status_code == 404
    assert response.json()["detail"] == f"User with id 999999 not found"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["content_type", "body"],
    [
        (
            "post",
            {
                "url": "https://www.github.com/",
                "title": "github",
                "thumbnail": "",
                "favicon": "",
                "description": "",
                "bookmark": False,
                "video_length": 0,
                "body": "",
                "tags": ["temp"],
            },
        )
    ],
)
async def test_save_content_fail_with_exists_content(
    auth_client, test_user_persist_with_content, content_type, body
):
    """
    이미 저장된 콘텐츠를 다시 저장 -> 400 Bad Request
    """
    body["user_id"] = test_user_persist_with_content.id

    response = await auth_client.post(
        f"/api/contents/save?content_type={content_type}", json=body
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Content already exists"


@pytest.mark.asyncio
async def test_delete_content_success(
    auth_client, test_user_persist_with_content, db_session
):
    """
    콘텐츠 삭제 성공 -> 200
    DB에서 해당 콘텐츠가 실제로 삭제되었는지 확인
    """
    async with db_session as session:
        result = await session.execute(
            select(Content).where(Content.user_id == test_user_persist_with_content.id)
        )
        db_content = result.unique().scalars().first()
        content_id = db_content.id

    response = await auth_client.delete(f"/api/contents/{content_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "success"

    async with db_session as session:
        result = await session.execute(select(Content).where(Content.id == content_id))
        db_content = result.unique().scalars().first()
        assert not db_content


@pytest.mark.asyncio
async def test_delete_content_fail(auth_client):
    """
    존재하지 않는 콘텐츠 ID 삭제 -> 404 Not Found
    """
    fake_content_id = 999999

    response = await auth_client.delete(f"/api/contents/{fake_content_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Content not found"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "field",
    [
        "id",
        "title",
        "url",
        "thumbnail",
        "favicon",
        "description",
        "bookmark",
        "video_length",
        "body",
        "tags",
        "created_at",
        "type",
    ],
)
async def test_get_all_contents_success(
    auth_client, test_user_persist_with_content, db_session, field
):
    """
    사용자의 전체 콘텐츠 조회 성공 -> 200
    응답이 리스트 형식이며, 콘텐츠 수와 필드들이 정확히 포함되는지 확인
    """
    response = await auth_client.get(
        f"/api/contents/user/{test_user_persist_with_content.id}/all"
    )

    async with db_session as session:
        result = await session.execute(
            select(Content).where(Content.user_id == test_user_persist_with_content.id)
        )
        db_content = result.scalars().all()
        content_len = len(db_content)

    response_json = response.json()

    assert response.status_code == 200
    assert isinstance(response_json, list)
    assert len(response_json) == content_len
    assert field in response_json[0]


@pytest.mark.asyncio
async def test_get_bookmarked_contents_success(
    auth_client, test_user_persist_with_content, db_session
):
    """
    북마크된 콘텐츠 조회 성공 테스트
    """
    response = await auth_client.get(
        f"/api/contents/bookmarks/user/{test_user_persist_with_content.id}"
    )

    response_json = response.json()

    assert response.status_code == 200
    assert isinstance(response_json, list)
    assert all(x["bookmark"] for x in response_json)


@pytest.mark.asyncio
async def test_toggle_bookmark_success(
    auth_client, test_user_persist_with_content, db_session
):
    """
    북마크 상태 토글 성공 테스트
    """
    async with db_session as session:
        result = await session.execute(
            select(Content).where(Content.user_id == test_user_persist_with_content.id)
        )

        db_content = result.unique().scalars().first()
        bookmarked = db_content.bookmark

    response = await auth_client.post(f"/api/contents/{db_content.id}/bookmark")

    assert response.status_code == 200
    assert response.json()["message"] == "success"

    async with db_session as session:
        result = await session.execute(
            select(Content).where(Content.user_id == test_user_persist_with_content.id)
        )

        db_content = result.unique().scalars().first()
        new_bookmarked = db_content.bookmark

    assert new_bookmarked != bookmarked


@pytest.mark.asyncio
async def test_edit_content_success(
    auth_client, test_user_persist_with_content, db_session
):
    """
    콘텐츠 수정 성공 테스트
    """
    async with db_session as session:
        result = await session.execute(
            select(Content)
            .where(Content.user_id == test_user_persist_with_content.id)
            .options(
                selectinload(Content.tags),
                joinedload(Content.video_metadata),
                joinedload(Content.post_metadata),
            )
        )

        db_content = result.unique().scalars().first()

    body = {
        "url": db_content.url,  # url은 못바꿈
        "title": "new_title",
        "thumbnail": "new_thumbnail",
        "favicon": db_content.favicon,  # favicon은 못바꿈
        "description": "new_description",
        "bookmark": not db_content.bookmark,
        "video_length": 0,
        "body": "",
        "tags": [x.tagname for x in db_content.tags],
    }

    response = await auth_client.put(
        f"/api/contents/{db_content.id}/user/{test_user_persist_with_content.id}",
        json=body,
    )

    assert response.status_code == 200

    async with db_session as session:
        result = await session.execute(
            select(Content).where(Content.id == db_content.id)
        )

        editted_content = result.unique().scalars().first()

    assert editted_content.title == "new_title"
    assert editted_content.thumbnail == "new_thumbnail"
    assert editted_content.description == "new_description"
    assert editted_content.bookmark != db_content.bookmark
    assert editted_content.bookmark != db_content.bookmark
