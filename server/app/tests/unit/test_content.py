import pytest
from app.models.content import Content
from sqlalchemy import and_, select


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
async def test_analyze_success(
    auth_client, test_user_persist, content_type, body, field
):
    """
    콘텐츠 분석 성공 시 200 확인 및
    각 필드(url, title, thumbnail 등)가 응답에 포함되는지 확인
    """
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
async def test_analyze_fail_with_invalid_url(
    auth_client, test_user_persist, content_type, body
):
    """
    존재하지 않는 url analyze시 422 Unprocessable Entitiy
    """
    body["user_id"] = test_user_persist.id

    response = await auth_client.post(
        f"/api/contents/analyze?content_type={content_type}", json=body
    )

    if content_type == "post":
        # 해당 url이 존재하지 않음
        assert response.status_code == 422
    else:
        # 해당 video id의 video가 존재하지 않음
        assert response.status_code == 404


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
    이미 존재하는 contents를 analyze하려할 때 400 Bad Request
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
