from copy import deepcopy
from httpx import ASGITransport, AsyncClient
import pytest


@pytest.mark.asyncio
async def test_video_analyze_success(auth_client, test_video_link):
  """
  video analyze api 테스트
  """
  # TODO
  assert True

@pytest.mark.asyncio
async def test_video_analyze_fail1(auth_client, test_video_link):
  """
  video_id 불일치 -> 실패
  """
  test_video_link["tag_count"] = 3
  test_video_link["detail_degree"] = 3
  
  async with AsyncClient(transport=ASGITransport(app=auth_client.app), base_url="http://test") as async_client:
    response = await async_client.post(
      "/api/videos/analyze",
      json = test_video_link  
    )
    
  assert response.status_code == 422,  f"video id does not match -> fail: {response.text}"
  
@pytest.mark.asyncio
async def test_video_analyze_fail2(auth_client, test_video_link):
  """
  tag_count < 1, tag_count ≥ 10, detail_degree not in [1,2,3,4,5] -> 실패
  """
  test_video_link["tag_count"] = 3
  test_video_link["detail_degree"] = 3
  
  async with AsyncClient(transport=ASGITransport(app=auth_client.app), base_url="http://test") as async_client:
    test_video_link_tmp = deepcopy(test_video_link)
    test_video_link_tmp["tag_count"] = 0
    response = await async_client.post(
      "/api/videos/analyze",
      json = test_video_link_tmp  
    )
    assert response.status_code == 422, f"tag_count must be ge=1, lt=10: {response.text}"
    
    test_video_link_tmp = deepcopy(test_video_link)
    test_video_link_tmp["tag_count"] = 10
    response = await async_client.post(
      "/api/videos/analyze",
      json = test_video_link_tmp  
    )
    assert response.status_code == 422, f"tag_count must be ge=1, lt=10: {response.text}"
    
    test_video_link_tmp = deepcopy(test_video_link)
    test_video_link_tmp["detail_degree"] = 0
    response = await async_client.post(
      "/api/videos/analyze",
      json = test_video_link_tmp  
    )
    assert response.status_code == 422, f"detail degree must be [1, 2, 3, 4, 5]: {response.text}"
    
    test_video_link_tmp = deepcopy(test_video_link)
    test_video_link_tmp["detail_degree"] = 6
    response = await async_client.post(
      "/api/videos/analyze",
      json = test_video_link_tmp  
    )
    assert response.status_code == 422, f"detail degree must be [1, 2, 3, 4, 5]: {response.text}"
    
    
    