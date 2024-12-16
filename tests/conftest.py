import asyncio
import os
import sys
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from app.config.main import settings
from app.database import Base, get_async_session
from app.main import app as fastapi_app

DB_URL = settings.postgres.TEST_DB_URL
engine = create_async_engine(DB_URL, poolclass=NullPool)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


fastapi_app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as async_client:
        yield async_client


@pytest.fixture(scope="function")
async def authenticated_async_client():
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as async_client:
        response = await async_client.post("/auth/token", json={
            "id": 123456789,
            "first_name": "Alice",
            "last_name": "Smith",
            "username": "alice_smith",
            "photo_url": "https://t.me/i/userpic/320/alice_smith.jpg",
            "auth_date": 1700000000,
            "hash": "8148c1689fdc140a4a7b6c2182718f49d80b69588986c9412d37bcef5e974c5a"
        })
        token = response.json().get("access_token")
        async_client.headers = {
            **async_client.headers,
            "Authorization": token,
        }
        yield async_client
