import random
import uuid
from typing import Any, AsyncGenerator

import faker
import pytest_asyncio
from app.db import get_db
from app.main import app as main_app
from app.models.base import Base
from app.models.content import Content, ContentTypeEnum
from app.models.content_tag import content_tag_association
from app.models.tag import Tag
from app.models.user import User
from app.util.auth import create_access_token
from config import get_settings
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

POSTGRES_TEST_DB_URL = "postgresql+asyncpg://test:1234@localhost:5432/test_db"

engine = create_async_engine(POSTGRES_TEST_DB_URL, future=True, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


@pytest_asyncio.fixture()
async def app() -> AsyncGenerator[FastAPI, Any]:
    _app = main_app
    yield _app
    await engine.dispose()


@pytest_asyncio.fixture()
async def db_session() -> AsyncGenerator[AsyncSession, Any]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture()
async def client(
    app: FastAPI, db_session: AsyncSession
) -> AsyncGenerator[AsyncClient, Any]:
    async def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db

    from httpx import ASGITransport

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()


@pytest_asyncio.fixture()
async def auth_client(client):
    settings = get_settings()
    access_token = create_access_token(settings, data={"sub": "test@example.com"})
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    yield client


f = faker.Faker("ko-KR")


@pytest_asyncio.fixture()
def oauth_id():
    return str(uuid.uuid4())


@pytest_asyncio.fixture()
def oauth_provider():
    return random.choice(["Google", "apple"])


@pytest_asyncio.fixture()
def test_video_url():
    return {
        "url": "https://youtu.be/rAE4tYftFfo?si=52kXe2o9wpk5VHnR",
        "tag_count": 0,
        "detail_degree": 0,
    }


@pytest_asyncio.fixture()
async def test_user_persist(db_session: AsyncSession, oauth_id, oauth_provider):
    # 신규 가입한 후 어떠한 활동도 하지 않은 user
    user = User(
        username=f.user_name(),
        oauth_id=oauth_id,
        oauth_provider=oauth_provider,
        email="test@example.com",
        profile_image=f.image_url(),
        is_premium=False,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest_asyncio.fixture()
async def test_google_user_persist(db_session: AsyncSession, oauth_id):
    # 신규 가입한 후 어떠한 활동도 하지 않은 user
    user = User(
        username=f.user_name(),
        oauth_id=oauth_id,
        oauth_provider="Google",
        email="test@example.com",
        profile_image=f.image_url(),
        is_premium=False,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest_asyncio.fixture()
async def test_apple_user_persist(db_session: AsyncSession, oauth_id):
    # 신규 가입한 후 어떠한 활동도 하지 않은 user
    user = User(
        username=f.user_name(),
        oauth_id=oauth_id,
        oauth_provider="apple",
        email="test@example.com",
        profile_image=f.image_url(),
        is_premium=False,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest_asyncio.fixture()
async def test_user_persist_with_content(
    test_google_user_persist,
    db_session: AsyncSession,
):
    # 신규 가입한 후 유효 content 저장한 user
    content1 = Content(
        url="https://www.github.com/",
        title="GitHub · Build software better, together.",
        description="GitHub is where over 100 million developers shape the future of software, together.",
        bookmark=False,
        thumbnail="https://github.githubassets.com/images/modules/open_graph/github-mark.png",
        favicon="https://github.com/favicon.ico",
        content_type=ContentTypeEnum.POST,
        user_id=test_google_user_persist.id,
    )

    content2 = Content(
        url="https://www.naver.com/",
        title="",
        description="",
        bookmark=True,
        thumbnail="",
        favicon="",
        content_type=ContentTypeEnum.POST,
        user_id=test_google_user_persist.id,
    )

    tag1 = Tag(
        tagname="programming",
        user_id=test_google_user_persist.id,
    )
    tag2 = Tag(
        tagname="github",
        user_id=test_google_user_persist.id,
    )
    tag3 = Tag(
        tagname="naver",
        user_id=test_google_user_persist.id,
    )

    db_session.add(content1)
    db_session.add(content2)

    db_session.add(tag1)
    db_session.add(tag2)
    db_session.add(tag3)

    await db_session.flush()

    await db_session.execute(
        insert(content_tag_association),
        {"content_id": content1.id, "tag_id": tag1.id},
    )
    await db_session.execute(
        insert(content_tag_association),
        {"content_id": content1.id, "tag_id": tag2.id},
    )
    await db_session.execute(
        insert(content_tag_association),
        {"content_id": content2.id, "tag_id": tag1.id},
    )
    await db_session.execute(
        insert(content_tag_association),
        {"content_id": content2.id, "tag_id": tag3.id},
    )

    await db_session.flush()
    await db_session.commit()

    return test_google_user_persist
