import random
import uuid
from typing import Any, Generator

import faker
import pytest
from app.db import get_db
from app.main import get_application
from app.models.base import Base
from app.models.content import Content, ContentTypeEnum
from app.models.content_tag import content_tag_association
from app.models.tag import Tag
from app.models.user import User
from app.models.video_metadata import VideoMetadata
from app.util.auth import create_access_token
from config import get_settings
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

POSTGRES_TEST_DB_URL = "postgresql+aysncpg://test:1234@localhost:5432/test_db"

engine = create_engine(POSTGRES_TEST_DB_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def app() -> Generator[FastAPI, Any, None]:
    _app = get_application()
    yield _app
    engine.dispose()


@pytest.fixture()
def db_session() -> Generator[Session, Any, None]:
    Base.metadata.create_all(engine)
    connection = engine.connect()
    session = TestSessionLocal(bind=connection)

    yield session

    session.rollback()
    session.close()
    connection.close()
    Base.metadata.drop_all(engine)


@pytest.fixture()
def client(app: FastAPI, db_session: Session) -> Generator[TestClient, Any, None]:
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        yield client


@pytest.fixture
def auth_client(client):
    settings = get_settings()
    access_token = create_access_token(settings, data={"sub": "test@example.com"})

    client.headers.update(
        {
            "Authorization": f"Bearer {access_token}",
        }
    )

    yield client


f = faker.Faker("ko-KR")


@pytest.fixture()
def oauth_id():
    return str(uuid.uuid4())


@pytest.fixture()
def oauth_provider():
    providers = ["Google", "Apple", "Kakao"]
    rand_idx = random.randrange(0, len(providers))

    return providers[rand_idx]


@pytest.fixture()
def test_user(oauth_id, oauth_provider):
    user = {
        "id": f.random_int(min=1, max=100),
        "username": f.user_name(),
        "oauth_id": oauth_id,
        "oauth_provider": oauth_provider,
        "email": "test@example.com",  # token 로직 때문에 고정
        "profile_image": f.image_url(),
    }

    return user


@pytest.fixture(scope="function")
def test_user_persist(db_session, oauth_id, oauth_provider):
    user = User(
        username=f.user_name(),
        oauth_id=oauth_id,
        oauth_provider=oauth_provider,
        email="test@example.com",
        profile_image=f.image_url(),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture()
def test_video_url():
    video = {
        "url": "https://youtu.be/rAE4tYftFfo?si=52kXe2o9wpk5VHnR",
        "tag_count": 0,  # test code에서 수정
        "detail_degree": 0,  # test code에서 수정
    }

    return video


@pytest.fixture(scope="function")
def test_user_with_video_and_tag(db_session, oauth_id, oauth_provider, test_video_url):
    """
    비디오와 태그를 저장한 테스트 유저 반환
    """
    user = User(
        username=f.user_name(),
        oauth_id=oauth_id,
        oauth_provider=oauth_provider,
        email="test@example.com",
        profile_image=f.image_url(),
    )
    db_session.add(user)
    db_session.flush()

    content = Content(
        url=test_video_url["url"],
        title=f.sentence(),
        thumbnail=f.image_url(),
        description=f.sentence(),
        bookmark=True,
        content_type=ContentTypeEnum.VIDEO,
        user_id=user.id,
    )
    db_session.add(content)
    db_session.flush()

    video_metadata = VideoMetadata(
        content_id=content.id,
        video_length="360",
    )
    db_session.add(video_metadata)

    tagnames = ["AI", "Machine Learning", "Tech"]
    tags = []
    for tagname in tagnames:
        tag = db_session.query(Tag).filter(Tag.tagname == tagname).first()
        if not tag:
            tag = Tag(tagname=tagname, user_id=user.id)
            db_session.add(tag)
            db_session.flush()
        tags.append(tag)

    for tag in tags:
        db_session.execute(
            content_tag_association.insert().values(
                content_id=content.id, tag_id=tag.id
            )
        )

    db_session.commit()

    return user
