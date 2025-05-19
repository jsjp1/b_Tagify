import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 20160  # 14days

    SECRET_KEY: str = "test_secret_key_12345"

    POSTGRES_USER: str = "test"
    POSTGRES_PASSWORD: str = "1234"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_DB: str = "test_db"

    YOUTUBE_API_KEY: str = "REAL_YOUTUBE_API_KEY"

    GOOGLE_IOS_CLIENT_ID: str = "GOOGLE_IOS_CLIENT_ID"
    GOOGLE_ANDROID_CLIENT_ID: str = "GOOGLE_ANDROID_CLIENT_ID"

    APPLE_CLIENT_ID_IOS: str = "com.ellipsoid.tagi"
    APPLE_CLIENT_ID_ANDROID: str = "com.ellipsoid.tagi.socialLogin"

    TEST_GOOGLE_ID_TOKEN: str = "TEST_GOOGLE_ID_TOKEN"
    TEST_GOOGLE_OAUTH_ID: str = "TEST_GOOGLE_OAUTH_ID"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )

    @property
    def apple_audiences(self) -> list[str]:
        return [self.APPLE_CLIENT_ID_IOS, self.APPLE_CLIENT_ID_ANDROID]


def get_settings():
    env_path = os.path.abspath(".env")
    return Settings(_env_file=env_path, _env_file_encoding="utf-8")
