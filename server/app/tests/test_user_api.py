from copy import deepcopy

import pytest
from httpx import ASGITransport, AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_db_connection(client):
    """
    db connection api 테스트
    """
    async with AsyncClient(
        transport=ASGITransport(app=client.app), base_url="http://test"
    ) as async_client:
        response = await async_client.get("/health/db")

        assert response.status_code == 200, f"DB Health Check Failed: {response.text}"
        assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_get_all_users(auth_client, test_user_persist):
    """
    모든 유저 가져오는 api 테스트
    """
    async with AsyncClient(
        transport=ASGITransport(app=auth_client.app), base_url="http://test"
    ) as async_client:
        response = await async_client.get(
            "/api/users/",
        )
        
        response_json = response.json()
        response_users = response_json["users"]
        
        assert response.status_code == 200, f"Get All Users API Failed: {response.text}"
        assert "users" in response_json
        assert isinstance(response_users, list)
        assert len(response_users) >= 1
        
        assert "username" in response_users[0]
        assert "oauth_provider" in response_users[0]
        assert "oauth_id" in response_users[0]
        assert "email" in response_users[0]
        assert "profile_image" in response_users[0]


@pytest.mark.asyncio
async def test_signup_success(client, test_user, db_session):
    """
    회원가입 api 테스트
    """
    async with AsyncClient(
        transport=ASGITransport(app=client.app), base_url="http://test"
    ) as async_client:
        response = await async_client.post(
            "/api/users/signup",
            json=test_user,
        )

        response_json = response.json()

        assert response.status_code == 200, f"User Sign Up API Failed: {response.text}"
        assert response_json["oauth_id"] == test_user["oauth_id"]
        assert response_json["email"] == test_user["email"]
        
        db_user = db_session.query(User).filter(User.oauth_id == test_user["oauth_id"]).first()
        assert db_user is not None, "User Signup fail"


@pytest.mark.asyncio
async def test_signup_fail(client, test_user):
    """
    email 형식을 지키지 않은 요청 reject
    """
    test_user["email"] = "invalidEmail"

    async with AsyncClient(
        transport=ASGITransport(app=client.app), base_url="http://test"
    ) as async_client:
        response = await async_client.post(
            "/api/users/signup",
            json=test_user,
        )

        assert (
            response.status_code == 422
        ), f"Email Check Validation Failed: {response.text}"


@pytest.mark.asyncio
async def test_signup_fail_oauth_null(client, test_user):
    """
    oauth_id 필드가 null이면 안됨
    """
    async with AsyncClient(
        transport=ASGITransport(app=client.app), base_url="http://test"
    ) as async_client:
        test_user_tmp = deepcopy(test_user)
        del test_user_tmp["oauth_id"]
        response1 = await async_client.post(
            "/api/users/signup",
            json=test_user_tmp,
        )
        assert response1.status_code == 422, f"Not Nullable data: {response1.text}"

        test_user_tmp = deepcopy(test_user)
        del test_user_tmp["username"]
        response2 = await async_client.post(
            "/api/users/signup",
            json=test_user_tmp,
        )
        assert response2.status_code == 422, f"Not Nullable data: {response2.text}"

        test_user_tmp = deepcopy(test_user)
        del test_user_tmp["oauth_provider"]
        response3 = await async_client.post(
            "/api/users/signup",
            json=test_user_tmp,
        )
        assert response3.status_code == 422, f"Not Nullable data: {response3.text}"


@pytest.mark.asyncio
async def test_signup_and_login_success(client, test_user):
    """
    회원가입 후 로그인
    """
    async with AsyncClient(
        transport=ASGITransport(app=client.app), base_url="http://test"
    ) as async_client:
        response = await async_client.post(
            "/api/users/signup",
            json=test_user,
        )

        login_user = {
            "oauth_id": test_user["oauth_id"],
            "email": test_user["email"],
        }

        response = await async_client.post(
            "/api/users/login",
            json=login_user,
        )

        response_json = response.json()

        assert response.status_code == 200, f"User Login API Failed: {response.text}"
        assert "access_token" in response_json
        assert "refresh_token" in response_json
        assert response_json["username"] == test_user["username"]
        assert response_json["oauth_provider"] == test_user["oauth_provider"]
        assert response_json["profile_image"] == test_user["profile_image"]
        assert response_json["oauth_id"] == test_user["oauth_id"]
        assert response_json["email"] == test_user["email"]


@pytest.mark.asyncio
async def test_signup_and_login_fail(client, test_user):
    """
    회원가입 후, 회원가입 시 사용한 oauth_id와 다른 oauth_id로 로그인 -> 실패
    """
    async with AsyncClient(
        transport=ASGITransport(app=client.app), base_url="http://test"
    ) as async_client:
        response = await async_client.post(
            "/api/users/signup",
            json=test_user,
        )

        login_user = {
            "oauth_id": "7777777_7777777",
            "email": test_user["email"],
        }

        response = await async_client.post(
            "/api/users/login",
            json=login_user,
        )

        assert (
            response.status_code == 400
        ), f"different oauth_id -> success error: {response.text}"
