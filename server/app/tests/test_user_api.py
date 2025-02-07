from copy import deepcopy
import pytest
from httpx import ASGITransport, AsyncClient

@pytest.mark.asyncio
async def test_db_connection(client):
  """
  db connection api 테스트
  """
  async with AsyncClient(transport=ASGITransport(app=client.app), base_url="http://test") as async_client:
    response = await async_client.get("/health/db")
    
  assert response.status_code == 200,  f"DB Health Check Failed: {response.text}"
  assert response.json() == {"status": "ok"}
  
@pytest.mark.asyncio
async def test_signup_success(client, test_user):
  """
  회원가입 api 테스트
  """
  async with AsyncClient(transport=ASGITransport(app=client.app), base_url="http://test") as async_client:
    response = await async_client.post(
      "/api/users/signup",
      json = test_user,
    )
    
  response_json = response.json()
  
  assert response.status_code == 200, f"User Sign Up API Failed: {response.text}"
  assert response_json["message"] == "success"
  assert response_json["created_user_profile"]["username"] == test_user["username"]
  assert response_json["created_user_profile"]["oauth_provider"] == test_user["oauth_provider"]
  assert response_json["created_user_profile"]["oauth_id"] == test_user["oauth_id"]
  assert response_json["created_user_profile"]["profile_image"] == test_user["profile_image"]
  assert response_json["created_user_profile"]["email"] == test_user["email"]
    
@pytest.mark.asyncio
async def test_signup_fail(client, test_user):
  """
  email 형식을 지키지 않은 요청 reject
  """
  test_user["email"] = "invalidEmail"
  
  async with AsyncClient(transport=ASGITransport(app=client.app), base_url="http://test") as async_client:
    response = await async_client.post(
      "/api/users/signup",
      json = test_user,
    )
    
  assert response.status_code == 422, f"Email Check Validation Failed: {response.text}"
    
@pytest.mark.asyncio
async def test_signup_fail_oauth_null(client, test_user):
  """
  oauth_id 필드가 null이면 안됨
  """
  
  async with AsyncClient(transport=ASGITransport(app=client.app), base_url="http://test") as async_client:
    test_user_tmp = deepcopy(test_user)
    del test_user_tmp["oauth_id"]
    response1 = await async_client.post(
      "/api/users/signup",
      json = test_user_tmp,
    )
    assert response1.status_code == 422, f"Not Nullable data: {response1.text}"
    
    test_user_tmp = deepcopy(test_user)
    del test_user_tmp["username"]
    response2 = await async_client.post(
      "/api/users/signup",
      json = test_user_tmp,
    )
    assert response2.status_code == 422, f"Not Nullable data: {response2.text}"
    
    test_user_tmp = deepcopy(test_user)
    del test_user_tmp["oauth_provider"]
    response3 = await async_client.post(
      "/api/users/signup",
      json = test_user_tmp,
    )
    assert response3.status_code == 422, f"Not Nullable data: {response3.text}"    
    
@pytest.mark.asyncio
async def test_signup_and_login_success(client, test_user):
  async with AsyncClient(transport=ASGITransport(app=client.app), base_url="http://test") as async_client:
    response = await async_client.post(
      "/api/users/signup",
      json = test_user,
    )
    
    login_user = {
      "oauth_id": test_user["oauth_id"],
      "email": test_user["email"],
    }
    
    response = await async_client.post(
      "/api/users/login",
      json = login_user,
    )
    
  response_json = response.json()
  
  assert response.status_code == 200, f"User Login API Failed: {response.text}"
  assert response_json["message"] == "success"
  assert "access_token" in response_json
  assert "refresh_token" in response_json
  assert response_json["existed_user_profile"]["username"] == test_user["username"]
  assert response_json["existed_user_profile"]["oauth_provider"] == test_user["oauth_provider"]
  assert response_json["existed_user_profile"]["profile_image"] == test_user["profile_image"]
  assert response_json["existed_user_profile"]["oauth_id"] == test_user["oauth_id"]
  assert response_json["existed_user_profile"]["email"] == test_user["email"]
  
@pytest.mark.asyncio
async def test_signup_and_login_fail(client, test_user):
  async with AsyncClient(transport=ASGITransport(app=client.app), base_url="http://test") as async_client:
    response = await async_client.post(
      "/api/users/signup",
      json = test_user,
    )
    
    login_user = {
      "oauth_id": "7777777_7777777",
      "email": test_user["email"],
    }
    
    response = await async_client.post(
      "/api/users/login",
      json = login_user,
    )
    
  assert response.status_code == 400, f"different oauth_id -> success error: {response.text}"
