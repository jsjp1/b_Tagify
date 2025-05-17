import pytest
from config import get_settings


@pytest.mark.asyncio
async def test_e2e_scenario1(server_client):
    """
    회원가입 및 로그인 잘되는지 확인
    스플래시 스크린에서 불러오는 api 잘되는지 확인
    ---
    튜토리얼 컨텐츠 2개
    태그 2개
    북마크 1개 -> 잘 저장되었는지 확인
    """
    settings = get_settings()  # 비밀값 가져오기 위함

    # 회원가입 및 로그인
    body = {
        "username": "test_user",
        "oauth_provider": "google",
        "oauth_id": settings.TEST_GOOGLE_OAUTH_ID,
        "email": "tjtpp009@gmail.com",
        "profile_image": "",
        "id_token": settings.TEST_GOOGLE_ID_TOKEN,
        "lang": "kr",
    }

    response1 = await server_client.post(
        "/api/users/login",
        json=body,
    )

    assert response1.status_code == 200
    login_response = response1.json()
    user_id = login_response["id"]

    server_client.headers.update(
        {"Authorization": f"Bearer {login_response['access_token']}"}
    )

    # 스플래시 스크린에서 수행되는 api request
    user_all_contents_response = await server_client.get(
        f"/api/contents/user/{user_id}/all"
    )
    assert user_all_contents_response.status_code == 200
    user_all_contents = user_all_contents_response.json()

    user_bookmarked_contents_response = await server_client.get(
        f"/api/contents/bookmarks/user/{user_id}"
    )
    assert user_bookmarked_contents_response.status_code == 200
    user_bookmarked_contents = user_bookmarked_contents_response.json()

    user_tags_response = await server_client.get(f"/api/tags/user/{user_id}")
    assert user_tags_response.status_code == 200
    user_tags = user_tags_response.json()

    user_tag_contents = []
    for tag in user_tags:
        tag_id = tag["id"]
        tag_name = tag["tagname"]

        _response = await server_client.get(f"/api/tags/{tag_id}/contents/all")
        assert _response.status_code == 200

        user_tag_contents.append({tag_name: _response.json()})

    tagname_list = [x["tagname"] for x in user_tags]
    content_name_list = [x["title"] for x in user_all_contents]
    bookmarked_content_name_list = [x["title"] for x in user_bookmarked_contents]

    assert sorted(tagname_list) == sorted(["Tagify", "튜토리얼"])
    assert sorted(content_name_list) == sorted(
        [
            "상단에 있는 앱 로고와 프로필 이미지를 모두 터치해보세요!",
            "Tagify를 이용하는 방법 🚀",
        ]
    )
    assert sorted(bookmarked_content_name_list) == sorted(["Tagify를 이용하는 방법 🚀"])
