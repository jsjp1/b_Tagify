import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
  ALGORITHM: str = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
  REFRESH_TOKEN_EXPIRE_MINUTES: int = 20160 # 14days
  
  SECRET_KEY: str = "test_secret_key_12345"
  
  POSTGRES_USER: str = "test"
  POSTGRES_PASSWORD: str = "1234"
  POSTGRES_HOST: str = "localhost"
  POSTGRES_DB: str = "test_db"
  
  YOUTUBE_API_KEY: str = "youtube_api_key"
  
  model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")
  
def get_settings():
  env_path = os.path.abspath(".env")
  return Settings(_env_file=env_path, _env_file_encoding="utf-8")