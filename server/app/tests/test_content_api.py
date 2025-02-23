import pytest
from app.models.content import Content
from app.models.user import User
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
@pytest.mark.parametrize("field", ["id", "url", "title", "thumbnail", "favicon", "description", "bookmark", "video_length", "body", "tags"])
async def test_get_all_contents(field, auth_client, test_user_with_video_and_tag):
    """
    get all contents api 테스트
    """
    test_user = test_user_with_video_and_tag
    async with AsyncClient(
      transport=ASGITransport(app=auth_client.app), base_url="http://test"
    ) as async_client:
        response = await async_client.get(
            f"/api/contents/user/all?user_id={test_user.id}",
            headers=auth_client.headers,
        )

        response_json = response.json()

        assert response.status_code == 200, "Get all contents api fail"
        assert isinstance(response_json, list)

        assert len(response_json) >= 1
        assert field in response_json[0]


@pytest.mark.asyncio
async def test_toggle_bookmark(auth_client, db_session, test_user_with_video_and_tag):
    """
    toggle bookmark api 테스트
    """
    test_user = test_user_with_video_and_tag

    content = db_session.query(Content).filter(Content.user.has(User.id == test_user.id)).first()

    async with AsyncClient(
      transport=ASGITransport(app=auth_client.app), base_url="http://test"
    ) as async_client:
        assert content.bookmark == True # fixture user 데이터가 bookmark를 True로 설정했음

        response = await async_client.post(
            f"/api/contents/{content.id}/bookmark",
            headers=auth_client.headers,
        )

        assert response.status_code == 200, "Toogle bookmark api fail"
        assert content.bookmark == False

        response = await async_client.post(
            f"/api/contents/{content.id}/bookmark",
            headers=auth_client.headers,
        )

        assert content.bookmark == True 


@pytest.mark.asyncio
@pytest.mark.parametrize("field", ["id", "url", "title", "thumbnail", "favicon", "description", "bookmark", "video_length", "body", "tags"])
async def test_get_all_bookmarked_contents_with_exist_data(field, auth_client, test_user_with_video_and_tag):
    """
    content와 tag 데이터가 존재하는 user -> get bookmarked contents api 테스트
    """
    test_user = test_user_with_video_and_tag

    async with AsyncClient(
      transport=ASGITransport(app=auth_client.app), base_url="http://test"
    ) as async_client:
        response = await async_client.get(
          f"/api/contents/bookmarks/user/{test_user.id}",
          headers=auth_client.headers,
        )

        response_json = response.json()

        assert response.status_code == 200, "Get bookmarked contents with exists data fail"
        assert isinstance(response_json, list)

        assert len(response_json) >= 1
        assert field in response_json[0]
  

@pytest.mark.asyncio
@pytest.mark.parametrize("field", ["id", "url", "title", "thumbnail", "favicon", "description", "bookmark", "video_length", "body", "tags"])
async def test_get_all_bookmarked_contents_with_no_data(field, auth_client, test_user_persist):
    """
    content와 tag 데이터가 없는 user -> get bookmarked contents api 테스트
    """
    async with AsyncClient(
      transport=ASGITransport(app=auth_client.app), base_url="http://test"
    ) as async_client:
        response = await async_client.get(
          f"/api/contents/bookmarks/user/{test_user_persist.id}",
          headers=auth_client.headers,
        )

        response_json = response.json()

        assert response.status_code == 200, "Get bookmarked contents with exists data fail"
        assert isinstance(response_json, list)

        assert len(response_json) == 0

