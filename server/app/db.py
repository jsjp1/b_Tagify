from typing import Any, AsyncGenerator

from app.models import Base
from config import get_settings
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

settings = get_settings()
DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:5432/{settings.POSTGRES_DB}"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,             
    max_overflow=20,          
    pool_timeout=30,         
    pool_recycle=1800,        
    pool_pre_ping=True,      
)
async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    async with async_session() as session, session.begin():
        try: 
            yield session    
        finally:
            await session.close()