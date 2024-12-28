import asyncio
import json
import os
import sys

import pytest

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import insert

from app.database import Base
from app.main import app as fastapi_app
from app.models.chats import Chats
from app.services.chats import get_chats_service
from app.utils import get_current_user_id
from tests.dependencies.database import async_session_maker, engine
from tests.dependencies.services import get_test_chats_service
from tests.dependencies.users import mock_get_current_user_id

fastapi_app.dependency_overrides[get_chats_service] = get_test_chats_service
fastapi_app.dependency_overrides[get_current_user_id] = mock_get_current_user_id


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
        add_chats = insert(Chats).values(chats)
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
