from copy import deepcopy

import pytest
from app.models.content import Content
from app.models.content_tag import content_tag_association
from app.models.video_metadata import VideoMetadata
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_video_analyze_success(
    auth_client, test_user_persist, test_video_url, db_session
):
    """
    video analyze api 테스트
    """
    test_video_url["lang"] = "ko"
    test_video_url["oauth_id"] = test_user_persist.oauth_id
    test_video_url["tag_count"] = 3
    test_video_url["detail_degree"] = 3

    async with AsyncClient(
        transport=ASGITransport(app=auth_client.app), base_url="http://test"
    ) as async_client:
        response = await async_client.post(
            "/api/contents/analyze?content_type=video",
            json=test_video_url,
            headers=auth_client.headers,
        )

    response_json = response.json()

    assert response.status_code == 200
    assert "content_id" in response.json()

    db_content = (
        db_session.query(Content)
        .filter(Content.id == response_json["content_id"])
        .first()
    )
    assert db_content is not None, "Content save fail"

    db_video_metadata = (
        db_session.query(VideoMetadata)
        .filter(VideoMetadata.content_id == response_json["content_id"])
        .first()
    )
    assert db_video_metadata is not None, "VideoMetadata save fail"

    result = db_session.execute(
        content_tag_association.select().where(
            content_tag_association.c.content_id == response_json["content_id"]
        )
    )
    tags = result.fetchall()
    assert len(tags) == test_video_url["tag_count"], "Tag save fail"


@pytest.mark.asyncio
async def test_video_analyze_fail1(auth_client, test_video_url):
    """
    video_id 불일치 -> 실패
    """
    test_video_url["tag_count"] = 3
    test_video_url["detail_degree"] = 3

    async with AsyncClient(
        transport=ASGITransport(app=auth_client.app), base_url="http://test"
    ) as async_client:
        response = await async_client.post(
            "/api/contents/analyze?content_type=video",
            json=test_video_url,
            headers=auth_client.headers,
        )

    assert (
        response.status_code == 422
    ), f"video id does not match -> fail: {response.text}"


@pytest.mark.asyncio
async def test_video_analyze_fail2(auth_client, test_video_url):
    """
    tag_count < 1, tag_count ≥ 10, detail_degree not in [1,2,3,4,5] -> 실패
    """
    test_video_url["tag_count"] = 3
    test_video_url["detail_degree"] = 3

    async with AsyncClient(
        transport=ASGITransport(app=auth_client.app), base_url="http://test"
    ) as async_client:
        test_video_url_tmp = deepcopy(test_video_url)
        test_video_url_tmp["tag_count"] = 0
        response = await async_client.post(
            "/api/contents/analyze?content_type=video",
            json=test_video_url_tmp,
            headers=auth_client.headers,
        )
        assert (
            response.status_code == 422
        ), f"tag_count must be ge=1, lt=10: {response.text}"

        test_video_url_tmp = deepcopy(test_video_url)
        test_video_url_tmp["tag_count"] = 10
        response = await async_client.post(
            "/api/contents/analyze?content_type=video",
            json=test_video_url_tmp,
            headers=auth_client.headers,
        )
        assert (
            response.status_code == 422
        ), f"tag_count must be ge=1, lt=10: {response.text}"

        test_video_url_tmp = deepcopy(test_video_url)
        test_video_url_tmp["detail_degree"] = 0
        response = await async_client.post(
            "/api/contents/analyze?content_type=video",
            json=test_video_url_tmp,
            headers=auth_client.headers,
        )
        assert (
            response.status_code == 422
        ), f"detail degree must be [1, 2, 3, 4, 5]: {response.text}"

        test_video_url_tmp = deepcopy(test_video_url)
        test_video_url_tmp["detail_degree"] = 6
        response = await async_client.post(
            "/api/contents/analyze?content_type=video",
            json=test_video_url_tmp,
            headers=auth_client.headers,
        )
        assert (
            response.status_code == 422
        ), f"detail degree must be [1, 2, 3, 4, 5]: {response.text}"


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
    ],
)
async def test_get_videos_success_with_exist_data(
    field, auth_client, test_user_with_video_and_tag
):
    """
    get user videos api 테스트
    """
    test_user = test_user_with_video_and_tag

    async with AsyncClient(
        transport=ASGITransport(app=auth_client.app), base_url="http://test"
    ) as async_client:
        response = await async_client.get(
            f"/api/contents/user/sub?content_type=video&user_id={test_user.id}",
            headers=auth_client.headers,
        )

        response_json = response.json()

        assert (
            response.status_code == 200
        ), f"Get User Videos API Failed: {response.text}"
        assert isinstance(response_json, list)
        assert len(response_json) >= 1

        assert field in response_json[0]
        assert isinstance(response_json[0]["tags"], list)
