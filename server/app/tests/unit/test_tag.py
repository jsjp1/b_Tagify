import pytest
from app.models.tag import Tag
from sqlalchemy import select


@pytest.mark.asyncio
async def test_save_content_with_deduplicated_tags_success(
    auth_client, test_user_persist, db_session
):
    """
    중복된 태그 저장시, 하나만 저장되는지 확인하는 테스트
    """
    bodies = [
        {
            "url": "https://www.github.com/",
            "title": "github",
            "thumbnail": "",
            "favicon": "",
            "description": "",
            "bookmark": False,
            "video_length": 0,
            "body": "",
            "tags": ["tag1", "tag2", "tag3", "tag100"],
        },
        {
            "url": "https://www.naver.com/",
            "title": "naver",
            "thumbnail": "",
            "favicon": "",
            "description": "",
            "bookmark": False,
            "video_length": 0,
            "body": "",
            "tags": ["tag1", "tag4", "tag100"],
        },
    ]

    for body in bodies:
        body["user_id"] = test_user_persist.id
        response = await auth_client.post(
            f"/api/contents/save?content_type=post", json=body
        )
        assert response.status_code == 200

    # 중복 없이 저장된 태그 수 확인
    expected_tags = set(["tag1", "tag2", "tag3", "tag4", "tag100"])

    async with db_session as session:
        result = await session.execute(
            select(Tag).where(Tag.user_id == test_user_persist.id)
        )
        db_tags = result.unique().scalars().all()

    assert len(db_tags) == len(expected_tags)
    assert set(tag.tagname for tag in db_tags) == expected_tags


@pytest.mark.asyncio
@pytest.mark.parametrize("field", ["id", "tagname", "color"])
async def test_get_user_tags_success(
    auth_client, test_user_persist_with_content, field
):
    """
    사용자 모든 태그 조회 성공 테스트
    """
    response = await auth_client.get(
        f"/api/tags/user/{test_user_persist_with_content.id}"
    )

    response_json = response.json()

    assert response.status_code == 200
    assert isinstance(response_json, list)
    assert len(response_json) == 3
    assert field in response_json[0]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "field",
    [
        "id",
        "url",
        "title",
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
async def test_get_tag_all_contents_success(
    auth_client, test_user_persist_with_content, db_session, field
):
    """
    각 태그에 연결된 콘텐츠 조회 시 필드 포함 여부 및 태그 포함 여부 확인
    """
    async with db_session as session:
        result = await session.execute(
            select(Tag).where(Tag.user_id == test_user_persist_with_content.id)
        )

        db_tags = result.unique().scalars().all()

    responses = [
        await auth_client.get(f"/api/tags/{tag.id}/contents/all") for tag in db_tags
    ]

    for i, response in enumerate(responses):
        response_json = response.json()

        assert response.status_code == 200
        assert isinstance(response_json, list)

        for content in response_json:
            assert field in content

            content_tags = content["tags"]
            assert db_tags[i].tagname in content_tags


@pytest.mark.asyncio
async def test_get_tag_all_contents_success_with_empty_tags(auth_client):
    """
    존재하지 않는 태그 ID -> [] 반환
    """
    fake_id = 999999
    response = await auth_client.get(f"/api/tags/{fake_id}/contents/all")

    assert response.status_code == 200
    assert response.json() == []
