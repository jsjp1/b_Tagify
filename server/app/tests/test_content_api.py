import pytest
from app.main import app as main_app
from app.models.content import Content
from app.models.user import User
from httpx import ASGITransport, AsyncClient
from sqlalchemy import and_
from sqlalchemy.future import select


@pytest.mark.asyncio(loop_scope="function")
@pytest.mark.parametrize(
    "field",
    [
        "id",
        "url",
        "title",
        "thumbnail",
        "favicon",
        "description",
        "bookmark",
        "video_length",
        "body",
        "tags",
    ],
)
async def test_get_all_contents(
    field, auth_client, test_user_with_video_and_tag, db_session
):
    """
    get all contents api 테스트
    """
    test_user = test_user_with_video_and_tag

    stmt = select(Content).filter(Content.user_id == test_user.id)
    result = await db_session.execute(stmt)
    contents = result.scalars().all()

    async with AsyncClient(
        transport=ASGITransport(app=main_app), base_url="http://test"
    ) as async_client:
        response = await async_client.get(
            f"/api/contents/user/{test_user.id}/all",
            headers=auth_client.headers,
        )

        response_json = response.json()

        assert response.status_code == 200, "Get all contents api fail"
        assert isinstance(response_json, list)

        assert len(response_json) >= 1
        assert field in response_json[0]


@pytest.mark.asyncio(loop_scope="function")
async def test_toggle_bookmark(auth_client, db_session, test_user_with_video_and_tag):
    """
    toggle bookmark api 테스트
    """
    test_user = test_user_with_video_and_tag

    # select 쿼리로 변경
    stmt = select(Content).filter(Content.user_id == test_user.id)
    result = await db_session.execute(stmt)
    content = result.scalars().first()

    async with AsyncClient(
        transport=ASGITransport(app=main_app), base_url="http://test"
    ) as async_client:
        assert (
            content.bookmark == True
        )  # fixture user 데이터가 bookmark를 True로 설정했음

        response = await async_client.post(
            f"/api/contents/{content.id}/bookmark",
            headers=auth_client.headers,
        )

        assert response.status_code == 200, "Toggle bookmark api fail"
        assert content.bookmark == False

        response = await async_client.post(
            f"/api/contents/{content.id}/bookmark",
            headers=auth_client.headers,
        )

        assert content.bookmark == True


@pytest.mark.asyncio(loop_scope="function")
@pytest.mark.parametrize(
    "field",
    [
        "id",
        "url",
        "title",
        "thumbnail",
        "favicon",
        "description",
        "bookmark",
        "video_length",
        "body",
        "tags",
    ],
)
async def test_get_all_bookmarked_contents_with_exist_data(
    field, auth_client, test_user_with_video_and_tag, db_session
):
    """
    content와 tag 데이터가 존재하는 user -> get bookmarked contents api 테스트
    """
    test_user = test_user_with_video_and_tag

    # select 쿼리로 변경
    stmt = select(Content).filter(
        and_(Content.user_id == test_user.id, Content.bookmark == True)
    )
    result = await db_session.execute(stmt)
    bookmarked_contents = result.scalars().all()

    async with AsyncClient(
        transport=ASGITransport(app=main_app), base_url="http://test"
    ) as async_client:
        response = await async_client.get(
            f"/api/contents/bookmarks/user/{test_user.id}",
            headers=auth_client.headers,
        )

        response_json = response.json()

        assert (
            response.status_code == 200
        ), "Get bookmarked contents with exists data fail"
        assert isinstance(response_json, list)

        assert len(response_json) >= 1
        assert field in response_json[0]


@pytest.mark.asyncio(loop_scope="function")
@pytest.mark.parametrize(
    "field",
    [
        "id",
        "url",
        "title",
        "thumbnail",
        "favicon",
        "description",
        "bookmark",
        "video_length",
        "body",
        "tags",
    ],
)
async def test_get_all_bookmarked_contents_with_no_data(
    field, auth_client, test_user_persist, db_session
):
    """
    content와 tag 데이터가 없는 user -> get bookmarked contents api 테스트
    """
    # select 쿼리로 변경
    stmt = select(Content).filter(
        Content.user_id == test_user_persist.id, Content.bookmark == True
    )
    result = await db_session.execute(stmt)
    bookmarked_contents = result.scalars().all()

    async with AsyncClient(
        transport=ASGITransport(app=main_app), base_url="http://test"
    ) as async_client:
        response = await async_client.get(
            f"/api/contents/bookmarks/user/{test_user_persist.id}",
            headers=auth_client.headers,
        )

        response_json = response.json()

        assert response.status_code == 200, "Get bookmarked contents with no data fail"
        assert isinstance(response_json, list)

        assert len(response_json) == 0
