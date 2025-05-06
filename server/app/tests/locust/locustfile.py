# locustfile.py
from locust import HttpUser, between, task


class WebsiteUser(HttpUser):
    # 사용자 사이의 요청 대기 시간 (1~3초 사이)
    wait_time = between(1, 3)

    def on_start(self):
        response = self.client.post("/api/users/login", json={"id_token": "test"})
        self.token = response.json()["access_token"]

    @task
    def get_contents(self):
        # /api/contents 경로에 GET 요청을 보냄
        self.client.get("/api/contents")

    @task
    def analyze_post(self):
        # /api/contents/analyze 에 POST 요청
        self.client.post(
            "/api/contents/analyze?content_type=post",
            json={
                "url": "https://www.github.com",
                "lang": "en",
                "tag_count": 3,
                "detail_degree": 3,
                "user_id": 1 
            },
        )        