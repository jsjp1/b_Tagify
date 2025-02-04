import os
from dotenv import load_dotenv

success = load_dotenv(dotenv_path=".env")
if not success: 
  print(".env file load failed")
  exit(-1)
  
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_DB = os.getenv("POSTGRES_DB")

print(POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_DB)

DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}"
print(DATABASE_URL)