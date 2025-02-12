import pytest
from httpx import ASGITransport, AsyncClient

from app.models.tag import Tag
from app.models.user_tag import user_tag_association


@pytest.mark.asyncio
async def test_get_tags_success_with_no_user(auth_client, test_user):
    """
    get user tags api 테스트
    """
    async with AsyncClient(
        transport=ASGITransport(app=auth_client.app), base_url="http://test"
    ) as async_client:
        response = await async_client.get(
            f"/api/tags/user?oauth_id={test_user['oauth_id']}",
        )

        response_json = response.json()

        # 없는 user(없는 oauth_id)더라도 200 status code 반환
        assert (
            response.status_code == 200
        ), f"Get User Videos API Failed: {response.text}"
        assert isinstance(response_json, list)

        if len(response_json) >= 1:
            assert "tag" in response_json
            assert "tag_id" in response_json
            
            
@pytest.mark.asyncio
async def test_get_tags_success_with_exist_user(auth_client, test_user_with_video_and_tag):
    """
    get user tags api 테스트
    """
    test_user = test_user_with_video_and_tag
    async with AsyncClient(
        transport=ASGITransport(app=auth_client.app), base_url="http://test"
    ) as async_client:
        response = await async_client.get(
            f"/api/tags/user?oauth_id={test_user.oauth_id}",
        )

        response_json = response.json()

        # 없는 user(없는 oauth_id)더라도 200 status code 반환
        assert (
            response.status_code == 200
        ), f"Get User Videos API Failed: {response.text}"
        assert isinstance(response_json, list)

        if len(response_json) >= 1:
            assert "tag" in response_json[0]
            assert "tag_id" in response_json[0]


@pytest.mark.asyncio
async def test_get_tag_videos(auth_client, test_user_with_video_and_tag, db_session):
    """
    태그 정보 -> 태그에 해당하는 video 가져오는 api 테스트
    """
    test_user = test_user_with_video_and_tag
    tag = db_session.query(Tag).join(user_tag_association).filter(user_tag_association.c.user_id == test_user.id).first()
    tag_id = tag.id
    
    async with AsyncClient(
        transport=ASGITransport(app=auth_client.app), base_url="http://test"
    ) as async_client:
        response = await async_client.get(
            f"/api/tags/{str(tag_id)}/contents?content_type=video"
        )
        
        response_json = response.json()
        
        assert response.status_code == 200, f"Get Tag Videos API Failed: {response.text}"
        assert isinstance(response_json, list)
        assert len(response_json) >= 1
        
        assert "url" in response_json[0]
        assert "title" in response_json[0]
        assert "thumbnail" in response_json[0]
        assert "video_length" in response_json[0]
        assert "body" in response_json[0] and response_json[0]["body"] == ""