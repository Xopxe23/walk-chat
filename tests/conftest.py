import asyncio
import json
import os
import sys
import uuid

from fastapi import HTTPException, status, Depends
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool, insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from fastapi.testclient import TestClient

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from app.chats.models import ChatRoom
from app.chats.filters import BaseFilter
from app.chats.router import get_current_user_id, api_key_header
from app.config.main import settings
from app.database import Base, get_async_session
from app.main import app as fastapi_app

DB_URL = settings.postgres.TEST_DB_URL
engine = create_async_engine(DB_URL, poolclass=NullPool)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def mock_get_current_user_id(token: str = Depends(api_key_header)) -> uuid.UUID:
    if token:
        user_id = "9c92aabb-3771-4756-97cc-b781371ff19a"
        return uuid.UUID(user_id)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
    )


class FakeFilter:
    limit: int = 10
    offset: int = 0


fastapi_app.dependency_overrides[get_async_session] = override_get_async_session
fastapi_app.dependency_overrides[get_current_user_id] = mock_get_current_user_id
fastapi_app.dependency_overrides[BaseFilter] = lambda: FakeFilter()


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    def open_mock_json(model: str):
        with open(f'tests/mocks/{model}.json', "r") as file:
            return json.load(file)

    chats = open_mock_json("chats")
    async with async_session_maker() as session:
        add_chats = insert(ChatRoom).values(chats)
        await session.execute(add_chats)
        await session.commit()


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as async_client:
        yield async_client


@pytest.fixture(scope="function")
async def authenticated_async_client():
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as async_client:
        async_client.headers = {
            **async_client.headers,
            "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
                             "eyJzdWIiOiI5YzkyYWFiYi0zNzcxLTQ3NTYtOTdjYy1iNzgxMzcxZmYxOWEiLCJleHAiOjE3NjYxMzQ5NzJ9."
                             "uW6ZV8dhu7Qdjia-oiIYWwmTY5eXnZs3LtjE8GDlNqs",
        }
        yield async_client


@pytest.fixture(scope="function")
def ws_authenticated_client():
    with TestClient(fastapi_app) as ws_client:
        ws_client.headers = {
            **ws_client.headers,
            "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
                             "eyJzdWIiOiI5YzkyYWFiYi0zNzcxLTQ3NTYtOTdjYy1iNzgxMzcxZmYxOWEiLCJleHAiOjE3NjYxMzQ5NzJ9."
                             "uW6ZV8dhu7Qdjia-oiIYWwmTY5eXnZs3LtjE8GDlNqs",
        }
        yield ws_client
