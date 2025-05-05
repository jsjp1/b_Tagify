from unittest.mock import AsyncMock, patch

import pytest
from app.models.user import User
from sqlalchemy import select


@pytest.mark.asyncio
async def test_db_connection(auth_client):
    """
    db connection api 테스트
    """
    response = await auth_client.get("/health/db", headers=auth_client.headers)

    assert response.status_code == 200, f"DB Health Check Failed: {response.text}"
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "field", ["username", "oauth_provider", "oauth_id", "email", "profile_image"]
)
async def test_get_all_users(field, auth_client, test_user_persist):
    """
    모든 유저 가져오는 api 테스트
    """
    response = await auth_client.get(
        "/api/users/",
        headers=auth_client.headers,
    )

    response_json = response.json()
    response_users = response_json["users"]

    assert response.status_code == 200, f"Get All Users API Failed: {response.text}"
    assert "users" in response_json
    assert isinstance(response_users, list)
    assert len(response_users) >= 1

    assert field in response_users[0]


@pytest.mark.asyncio
@patch("app.services.user.verify_google_token", new_callable=AsyncMock)
@pytest.mark.parametrize(
    "field",
    [
        "id",
        "username",
        "oauth_provider",
        "oauth_id",
        "email",
        "profile_image",
        "access_token",
        "refresh_token",
        "token_type",
        "is_premium",
    ],
)
async def test_login_google_new_user(mock_verify, field, client):
    """
    google oauth 로그인 테스트
    db에 신규 유저 저장 및 특정 필드 포함한 응답 반환하는지 확인
    verify_google_token은 외부 의존성이므로, mock 함수로 대체
    """
    mock_verify.return_value = {
        "sub": "google123",
        "email": "test@example.com",
        "name": "GoogleTestUser",
        "picture": "https://example.com/image.png",
    }

    user_login = {
        "id_token": "mock-id-token",
        "username": "GoogleTestUser",
        "oauth_provider": "Google",
        "oauth_id": "google123",
        "email": "test@example.com",
        "profile_image": "https://example.com/image.png",
        "lang": "kr",
    }

    response = await client.post(
        "/api/users/login",
        json=user_login,
    )

    response_json = response.json()

    assert response.status_code == 200, "User Google Login api failed"
    assert field in response_json
    for k in user_login.keys():
        if k in ("id_token", "lang"):
            continue

        assert user_login[k] == response_json[k]


@pytest.mark.asyncio
@patch("app.services.user.verify_google_token", new_callable=AsyncMock)
async def test_login_google_existing_user(
    mock_verify, client, test_google_user_persist
):
    """
    이미 존재하는 유저로 로그인할 경우, 새 유저를 만들지 않고 기존 유저 반환
    """
    mock_verify.return_value = {
        "sub": test_google_user_persist.oauth_id,
        "email": test_google_user_persist.email,
        "name": test_google_user_persist.username,
        "picture": test_google_user_persist.profile_image,
    }

    user_login = {
        "id_token": "mock-id-token",
        "username": test_google_user_persist.username,
        "oauth_provider": test_google_user_persist.oauth_provider,
        "oauth_id": test_google_user_persist.oauth_id,
        "email": test_google_user_persist.email,
        "profile_image": test_google_user_persist.profile_image,
        "lang": "kr",
    }

    response = await client.post("/api/users/login", json=user_login)
    response_json = response.json()

    assert response.status_code == 200
    assert response_json["id"] == test_google_user_persist.id
    assert response_json["email"] == test_google_user_persist.email


@pytest.mark.asyncio
@patch("app.services.user.verify_apple_token", new_callable=AsyncMock)
@pytest.mark.parametrize(
    "field",
    [
        "id",
        "username",
        "oauth_provider",
        "oauth_id",
        "email",
        "profile_image",
        "access_token",
        "refresh_token",
        "token_type",
        "is_premium",
    ],
)
async def test_login_apple_new_user(mock_verify, field, client):
    """
    Apple OAuth 로그인 테스트
    db에 신규 유저 저장 및 특정 필드 포함한 응답 반환하는지 확인
    verify_apple_token은 외부 의존성이므로, mock 함수로 대체
    """
    mock_verify.return_value = {
        "sub": "apple123",
        "email": "apple@example.com",
    }

    user_login = {
        "id_token": "fake.header.payload",
        "username": "AppleTestUser",
        "oauth_provider": "Apple",
        "oauth_id": "apple123",
        "email": "apple@example.com",
        "profile_image": "https://example.com/apple.png",
        "lang": "kr",
    }

    response = await client.post("/api/users/login", json=user_login)
    response_json = response.json()

    assert response.status_code == 200
    assert field in response_json
    for k in user_login:
        if k in ("id_token", "lang"):
            continue

        assert k in response_json
        assert user_login[k] == response_json[k]


@pytest.mark.asyncio
@patch("app.services.user.verify_apple_token", new_callable=AsyncMock)
async def test_login_apple_existing_user(mock_verify, client, test_apple_user_persist):
    """
    이미 존재하는 Apple 유저로 로그인할 경우, 새 유저를 만들지 않고 기존 유저 반환
    """
    mock_verify.return_value = {
        "sub": test_apple_user_persist.oauth_id,
        "email": test_apple_user_persist.email,
    }

    user_login = {
        "id_token": "fake.header.payload",
        "username": test_apple_user_persist.username,
        "oauth_provider": test_apple_user_persist.oauth_provider,
        "oauth_id": test_apple_user_persist.oauth_id,
        "email": test_apple_user_persist.email,
        "profile_image": test_apple_user_persist.profile_image,
        "lang": "kr",
    }

    response = await client.post("/api/users/login", json=user_login)
    response_json = response.json()

    assert response.status_code == 200
    assert response_json["id"] == test_apple_user_persist.id
    assert response_json["email"] == test_apple_user_persist.email


@pytest.mark.asyncio
@patch("app.services.user.verify_google_token", new_callable=AsyncMock)
async def test_login_google_invalid_token(mock_verify, client):
    """
    Google OAuth 로그인 시, 토큰에 'sub'이 없으면 400 오류 발생
    """
    mock_verify.return_value = {
        # 'sub' 누락
        "email": "invalid@example.com",
        "name": "NoSubUser",
    }

    user_login = {
        "id_token": "mock-id-token",
        "username": "NoSubUser",
        "oauth_provider": "Google",
        "oauth_id": "doesnotmatter",
        "email": "invalid@example.com",
        "profile_image": "https://example.com/fake.png",
        "lang": "kr",
    }

    response = await client.post("/api/users/login", json=user_login)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid Google ID Token"


@pytest.mark.asyncio
@patch("app.services.user.verify_apple_token", new_callable=AsyncMock)
async def test_login_apple_invalid_token(mock_verify, client):
    """
    Apple OAuth 로그인 시, 'sub'가 없으면 400 오류 발생
    """
    mock_verify.return_value = {
        # 'sub' 누락
        "email": "apple_invalid@example.com"
    }

    user_login = {
        "id_token": "fake.header.payload",
        "username": "NoSubApple",
        "oauth_provider": "apple",
        "oauth_id": "anything",
        "email": "apple_invalid@example.com",
        "profile_image": "https://example.com/apple.png",
        "lang": "kr",
    }

    response = await client.post("/api/users/login", json=user_login)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid Apple ID Token"


@pytest.mark.asyncio
@patch("app.services.user.verify_google_token", new_callable=AsyncMock)
async def test_refresh_token_success(mock_verify, client, test_google_user_persist):
    """
    유효한 refresh_token을 사용하여 access_token 재발급 테스트
    """
    mock_verify.return_value = {
        "sub": test_google_user_persist.oauth_id,
        "email": test_google_user_persist.email,
        "name": test_google_user_persist.username,
        "picture": test_google_user_persist.profile_image,
    }

    login_data = {
        "id_token": "mock-id-token",
        "username": test_google_user_persist.username,
        "oauth_provider": test_google_user_persist.oauth_provider,
        "oauth_id": test_google_user_persist.oauth_id,
        "email": test_google_user_persist.email,
        "profile_image": test_google_user_persist.profile_image,
        "lang": "kr",
    }

    response = await client.post("/api/users/login", json=login_data)
    assert response.status_code == 200

    response_json = response.json()
    refresh_token = response_json["refresh_token"]
    assert isinstance(refresh_token, str)

    response = await client.post(
        "/api/users/token/refresh", json={"refresh_token": refresh_token}
    )

    assert response.status_code == 200
    new_access_token = response.json()["tokens"]["access_token"]
    new_refresh_token = response.json()["tokens"]["refresh_token"]

    assert isinstance(new_access_token, str)
    assert (
        new_access_token != response_json["access_token"]
    ), "Refresh token did not issue a new access_token"
    assert (
        new_refresh_token != response_json["refresh_token"]
    ), "Refresh token did not issue a new refresh_token"


@pytest.mark.asyncio
async def test_refresh_token_missing(client):
    """
    refresh_token 누락 시 422 Validation Error
    """
    response = await client.post("/api/users/token/refresh", json={})
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, list)
    assert detail[0]["msg"].startswith("Field required")


@pytest.mark.asyncio
async def test_refresh_token_invalid(client):
    """
    잘못된 refresh_token 사용 시 실패 (예: 401 Unauthorized)
    """
    response = await client.post(
        "/api/users/token/refresh", json={"refresh_token": "invalid.token"}
    )

    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_update_user_name_success(auth_client, test_user_persist):
    """
    유저의 username을 업데이트하는 API 테스트 (성공 케이스)
    """
    new_name = "UpdatedName"

    response = await auth_client.put(
        f"/api/users/name/{test_user_persist.id}", json={"username": new_name}
    )

    response_json = response.json()

    assert response.status_code == 200, "Update User name Api failed"
    assert "id" in response_json
    assert response_json["id"] == test_user_persist.id


@pytest.mark.asyncio
async def test_update_user_name_validation_error(auth_client, test_user_persist):
    """
    username이 없는 경우 422 Validation Error 발생
    """
    response = await auth_client.put(
        f"/api/users/name/{test_user_persist.id}", json={}  # username 빠짐
    )

    assert response.status_code == 422
    response_json = response.json()
    assert "detail" in response_json
    assert response_json["detail"][0]["loc"][-1] == "username"


@pytest.mark.asyncio
async def test_update_user_name_invalid_user(auth_client):
    """
    존재하지 않는 user_id인 경우 정상 처리인지 확인 (예: 404 혹은 200)
    """
    invalid_user_id = 999999
    response = await auth_client.put(
        f"/api/users/name/{invalid_user_id}", json={"username": "testUser"}
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_update_profile_image_success(auth_client, test_user_persist):
    """
    유저의 profile_image를 변경하는 API 테스트 (성공 케이스)
    """
    new_image_url = "https://example.com/new_profile.png"

    response = await auth_client.put(
        f"/api/users/profile_image/{test_user_persist.id}",
        json={"profile_image": new_image_url},
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["id"] == test_user_persist.id


@pytest.mark.asyncio
async def test_update_profile_image_validation_error(auth_client, test_user_persist):
    """
    profile_image가 body에 없을 경우 422 Validation Error
    """
    response = await auth_client.put(
        f"/api/users/profile_image/{test_user_persist.id}", json={}
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail[0]["loc"][-1] == "profile_image"
    assert detail[0]["msg"].startswith("Field required")


@pytest.mark.asyncio
async def test_update_profile_image_invalid_user(auth_client):
    """
    존재하지 않는 user_id로 요청했을 경우 에러 or graceful 처리
    """
    fake_user_id = 999999
    response = await auth_client.put(
        f"/api/users/profile_image/{fake_user_id}",
        json={"profile_image": "https://example.com/ghost.png"},
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_delete_user_success(auth_client, test_user_persist, db_session):
    """
    사용자 삭제 후 제대로 삭제됐는지 확인
    """
    response = await auth_client.post(
        f"/api/users/me/delete",
        json={"id": test_user_persist.id, "reason": ""},
    )

    assert response.status_code == 200
    assert "id" in response.json()
    assert test_user_persist.id == response.json()["id"]

    async with db_session as session:
        result = await session.execute(
            select(User).where(User.id == test_user_persist.id)
        )
        user = result.scalar_one_or_none()
        assert user is None


@pytest.mark.asyncio
async def test_delete_user_fail(auth_client, test_user_persist):
    """
    없는 사용자 삭제하려고 했을 때 실패, 400 Error
    """
    fake_id = 999999
    response = await auth_client.post(
        f"/api/users/me/delete",
        json={"id": fake_id, "reason": ""},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == f"User with id {fake_id} not found"


@pytest.mark.asyncio
async def test_update_premium_success(auth_client, test_user_persist, db_session):
    """
    사용자 프리미엄 업그레이드 성공
    """
    response = await auth_client.put(
        f"/api/users/premium/{test_user_persist.id}",
    )

    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["id"] == test_user_persist.id

    async with db_session as session:
        result = await session.execute(
            select(User).where(User.id == test_user_persist.id)
        )
        user = result.scalar_one_or_none()
        assert user.is_premium
