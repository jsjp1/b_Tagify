import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
  ALGORITHM: str = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
  REFRESH_TOKEN_EXPIRE_MINUTES: int = 20160 # 14days
  
  SECRET_KEY: str
  
  POSTGRES_USER: str
  POSTGRES_PASSWORD: str
  POSTGRES_HOST: str
  POSTGRES_DB: str
  
  model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")
  
def get_settings():
  env_path = os.path.abspath(".env")
  return Settings(_env_file=env_path, _env_file_encoding="utf-8")