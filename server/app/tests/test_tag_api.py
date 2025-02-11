from httpx import ASGITransport, AsyncClient
import pytest

@pytest.mark.asyncio
async def test_get_tags_success(auth_client, test_user):
  """
  get user tags api 테스트
  """
  async with AsyncClient(transport=ASGITransport(app=auth_client.app), base_url="http://test") as async_client:
    response = await async_client.get(
      f"/api/tags/user?oauth_id={test_user['oauth_id']}",
    )
    
    response_json = response.json()
    
    # 없는 user(없는 oauth_id)더라도 200 status code 반환
    assert response.status_code == 200, f"Get User Videos API Failed: {response.text}"
    assert isinstance(response_json, list)

    if len(response_json) >= 1:
      assert "tag" in response_json
      assert "tag_id" in response_json