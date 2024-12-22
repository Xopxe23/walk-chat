import uuid
from typing import Optional, Protocol

import jwt
from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect
from fastapi.security import APIKeyHeader

from app.chats.manager import get_ws_manager
from app.chats.schemas import ChatCreateSchema, ChatRoomOutSchema, ChatRoomSchema
from app.chats.services import get_chat_service
from app.config.main import settings
from app.exceptions.auth import InvalidTokenException
from app.exceptions.common import NotFoundException

router = APIRouter(
    prefix="/chats",
    tags=["Chats"],
)

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def get_current_user_id(token: str = Depends(api_key_header)) -> uuid.UUID:
    try:
        payload = jwt.decode(token, settings.secret.JWT_SECRET, algorithms=[settings.secret.ALGORITHM])
        user_id: uuid.UUID = payload.get("sub")
        if user_id is None:
            raise InvalidTokenException
        return user_id
    except jwt.PyJWTError:
        raise InvalidTokenException


class ChatServiceInterface(Protocol):

    async def get_my_chats(self, user_id: uuid.UUID) -> list[ChatRoomSchema]:
        ...

    async def get_chat_by_id(self, chat_id: uuid.UUID) -> Optional[ChatRoomSchema]:
        ...

    async def create_chat(self, chat_data: ChatCreateSchema) -> ChatRoomSchema:
        ...


class WSManagerInterface(Protocol):
    async def connect(self, chat_id: uuid.UUID, websocket: WebSocket):
        ...

    async def disconnect(self, chat_id: uuid.UUID, websocket: WebSocket):
        ...

    async def send_message(self, chat_id: uuid.UUID, message: str):
        ...


@router.get("/my")
async def get_my_chats(
        user_id: uuid.UUID = Depends(get_current_user_id),
        chat_service: ChatServiceInterface = Depends(get_chat_service),
) -> list[ChatRoomSchema]:
    chats = await chat_service.get_my_chats(user_id)
    return chats


@router.post("/create_chat")
async def create_chat(
        chat_create_data: ChatCreateSchema,
        chat_service: ChatServiceInterface = Depends(get_chat_service),
) -> ChatRoomSchema:
    chat = await chat_service.create_chat(chat_create_data)
    return chat


@router.websocket("/ws/{chat_id}/")
async def connect_to_chat_by_id(
        chat_id: uuid.UUID,
        websocket: WebSocket,
        ws_manager: WSManagerInterface = Depends(get_ws_manager),
        chat_service: ChatServiceInterface = Depends(get_chat_service),
) -> None:
    token = websocket.headers.get("Authorization")
    user_id = get_current_user_id(token)
    chat = await chat_service.get_chat_by_id(chat_id)
    if not chat:
        raise NotFoundException
    chat_users = (str(chat.user1_id), str(chat.user2_id))
    if user_id not in chat_users:
        raise NotFoundException
    await ws_manager.connect(chat_id, websocket)
    try:
        while True:
            message = await websocket.receive_text()  # Ожидание входящего сообщения
            await ws_manager.send_message(chat_id, user_id, message)  # Отправка сообщения всем в чате
    except WebSocketDisconnect:
        await ws_manager.disconnect(chat_id, websocket)
