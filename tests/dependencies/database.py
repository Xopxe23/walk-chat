from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.configs.main import settings

DB_URL = settings.postgres.TEST_DB_URL
engine = create_async_engine(DB_URL, poolclass=NullPool)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


def get_test_session_maker():
    return async_session_maker
