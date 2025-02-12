def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "FastAPI Version 0.115.6"}


def test_users_endpoint(client):
    response = client.get("/api/users/endpoint_test")
    assert response.status_code == 200
    assert response.json() == {"message": "ok"}


def test_contents_endpoint(client):
    response = client.get("/api/contents/endpoint_test")
    assert response.status_code == 200
    assert response.json() == {"message": "ok"}
