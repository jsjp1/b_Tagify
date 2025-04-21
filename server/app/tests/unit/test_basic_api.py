import pytest


@pytest.mark.asyncio
async def test_root(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "FastAPI Version 0.115.6"}


@pytest.mark.asyncio
async def test_users_endpoint(auth_client):
    response = await auth_client.get("/api/users/endpoint_test")
    assert response.status_code == 200
    assert response.json() == {"message": "ok"}


@pytest.mark.asyncio
async def test_contents_endpoint(auth_client):
    response = await auth_client.get("/api/contents/endpoint_test")
    assert response.status_code == 200
    assert response.json() == {"message": "ok"}
