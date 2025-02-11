from copy import deepcopy
from httpx import ASGITransport, AsyncClient
import pytest


@pytest.mark.asyncio
async def test_video_analyze_success(auth_client, test_user_persist, test_video_url):
  """
  video analyze api 테스트
  """
  # TODO
  test_video_url["oauth_id"] = test_user_persist.oauth_id
  test_video_url["tag_count"] = 3
  test_video_url["detail_degree"] = 3
  async with AsyncClient(transport=ASGITransport(app=auth_client.app), base_url="http://test") as async_client:
    response = await async_client.post(
      "/api/videos/analyze",
      json = test_video_url  
    )
    
  assert response.status_code == 200
  assert "video_id" in response.json()

@pytest.mark.asyncio
async def test_video_analyze_fail1(auth_client, test_video_url):
  """
  video_id 불일치 -> 실패
  """
  test_video_url["tag_count"] = 3
  test_video_url["detail_degree"] = 3
  
  async with AsyncClient(transport=ASGITransport(app=auth_client.app), base_url="http://test") as async_client:
    response = await async_client.post(
      "/api/videos/analyze",
      json = test_video_url  
    )
    
  assert response.status_code == 422,  f"video id does not match -> fail: {response.text}"
  
@pytest.mark.asyncio
async def test_video_analyze_fail2(auth_client, test_video_url):
  """
  tag_count < 1, tag_count ≥ 10, detail_degree not in [1,2,3,4,5] -> 실패
  """
  test_video_url["tag_count"] = 3
  test_video_url["detail_degree"] = 3
  
  async with AsyncClient(transport=ASGITransport(app=auth_client.app), base_url="http://test") as async_client:
    test_video_url_tmp = deepcopy(test_video_url)
    test_video_url_tmp["tag_count"] = 0
    response = await async_client.post(
      "/api/videos/analyze",
      json = test_video_url_tmp  
    )
    assert response.status_code == 422, f"tag_count must be ge=1, lt=10: {response.text}"
    
    test_video_url_tmp = deepcopy(test_video_url)
    test_video_url_tmp["tag_count"] = 10
    response = await async_client.post(
      "/api/videos/analyze",
      json = test_video_url_tmp  
    )
    assert response.status_code == 422, f"tag_count must be ge=1, lt=10: {response.text}"
    
    test_video_url_tmp = deepcopy(test_video_url)
    test_video_url_tmp["detail_degree"] = 0
    response = await async_client.post(
      "/api/videos/analyze",
      json = test_video_url_tmp  
    )
    assert response.status_code == 422, f"detail degree must be [1, 2, 3, 4, 5]: {response.text}"
    
    test_video_url_tmp = deepcopy(test_video_url)
    test_video_url_tmp["detail_degree"] = 6
    response = await async_client.post(
      "/api/videos/analyze",
      json = test_video_url_tmp  
    )
    assert response.status_code == 422, f"detail degree must be [1, 2, 3, 4, 5]: {response.text}"
    
@pytest.mark.asyncio
async def test_get_videos_success(auth_client, test_user):
  """
  get user videos api 테스트
  """
  async with AsyncClient(transport=ASGITransport(app=auth_client.app), base_url="http://test") as async_client:
    response = await async_client.get(
      f"/api/videos/user?oauth_id={test_user['oauth_id']}",
    )
    
    response_json = response.json()
    
    # 없는 user(없는 oauth_id)더라도 200 status code 반환
    assert response.status_code == 200, f"Get User Videos API Failed: {response.text}"
    assert isinstance(response_json, list)

    if len(response_json) >= 1:
      assert "title" in response_json
      assert "url" in response_json
      assert "thumbnail" in response_json
      assert "summation" in response_json
      assert "video_length" in response_json
      assert "tags" in response_json
      assert isinstance(response_json["tags"], list)