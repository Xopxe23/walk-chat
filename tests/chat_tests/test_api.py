import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect


async def test_get_my_chats(
        async_client: AsyncClient,
        authenticated_async_client: AsyncClient,
):
    response = await async_client.get(url="/chats/my")
    assert response.status_code == 401
    response = await authenticated_async_client.get(url="/chats/my")
    assert response.status_code == 200
    chats = response.json()
    assert len(chats) == 2


def test_ws_get_my_chats(
        ws_authenticated_client: TestClient,
):
    with ws_authenticated_client.websocket_connect("chats/ws/my") as ws:
        assert ws
    ws_authenticated_client.headers.pop("Authorization")
    with pytest.raises(WebSocketDisconnect):
        with ws_authenticated_client.websocket_connect("chats/ws/my"):
            pass


def test_ws_get_chat_messages(
        ws_authenticated_client: TestClient,
):
    chat_id = "ddf79876-07e4-4340-af35-a44daa778c19"
    with ws_authenticated_client.websocket_connect(f"chats/ws/{chat_id}") as ws:
        ws.send_text("Здорова брательник")
        message = ws.receive_json()
        assert message["chat_id"] == chat_id


async def test_create_chat(
        async_client: AsyncClient,
):
    user_ids = {
        "user1_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "user2_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    }
    response = await async_client.post(url="/chats/create_chat", json=user_ids)
    assert response.status_code == 200
    chat = response.json()
    assert user_ids["user1_id"] == chat["user1_id"]
