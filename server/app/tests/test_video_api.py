from copy import deepcopy
from httpx import ASGITransport, AsyncClient
import pytest

@pytest.mark.asyncio
async def test_video_analyze_success(client, test_video_link):
  """
  video analyze api 테스트
  """
  test_video_link["tag_count"] = 3
  test_video_link["detail_degree"] = 3
  
  async with AsyncClient(transport=ASGITransport(app=client.app), base_url="http://test") as async_client:
    response = await async_client.post(
      "/api/videos/analyze",
      json = test_video_link  
    )
    
  response_json = response.json()
    
  assert response.status_code == 200,  f"Video Analyze API fail: {response.text}"
  assert response_json["message"] == "success"
  assert len(response_json["tags"]) == test_video_link["tag_count"]
  
@pytest.mark.asyncio
async def test_video_analyze_fail1(client, test_video_link):
  """
  tag_count < 1, tag_count ≥ 10, detail_degree not in [1,2,3,4,5] -> 실패
  """
  test_video_link["tag_count"] = 3
  test_video_link["detail_degree"] = 3
  
  async with AsyncClient(transport=ASGITransport(app=client.app), base_url="http://test") as async_client:
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
    
    
    