import uuid
from typing import Optional, Protocol

import jwt
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.security import APIKeyHeader

from app.chats.filters import BaseFilter
from app.chats.manager import get_ws_manager
from app.chats.schemas import ChatCreateSchema, ChatRoomSchema, MessageSchema
from app.chats.services import get_chat_service
from app.config.main import settings
from app.exceptions.auth import InvalidTokenException
from app.exceptions.chat import ChatAccessForbiddenException, ChatNotFoundException

router = APIRouter(
    prefix="/chats",
    tags=["Chats"],
)

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def get_current_user_id(token: str = Depends(api_key_header)) -> uuid.UUID:
    try:
        payload = jwt.decode(token, settings.secret.JWT_SECRET, algorithms=[settings.secret.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise InvalidTokenException
        return uuid.UUID(user_id)
    except jwt.PyJWTError:
        raise InvalidTokenException


class ChatServiceInterface(Protocol):

    async def get_my_chats(self, user_id: uuid.UUID, filters: BaseFilter) -> list[ChatRoomSchema]:
        ...

    async def get_chat_by_id(self, chat_id: uuid.UUID) -> Optional[ChatRoomSchema]:
        ...

    async def create_chat(self, chat_data: ChatCreateSchema) -> ChatRoomSchema:
        ...

    async def get_chat_messages(self, chat_id: uuid.UUID, filters: BaseFilter) -> list[MessageSchema]:
        ...


class WSManagerInterface(Protocol):
    async def connect(self, connection_id: uuid.UUID, websocket: WebSocket):
        ...

    async def disconnect(self, connection_id: uuid.UUID, websocket: WebSocket):
        ...

    async def send_message(self, chat_id: uuid.UUID, message: str):
        ...

    async def send_chat(self, user_ids: list[uuid.UUID], new_chat: ChatRoomSchema):
        ...


@router.get("/my")
async def get_my_chats(
        user_id: uuid.UUID = Depends(get_current_user_id),
        filters: BaseFilter = Depends(),
        chat_service: ChatServiceInterface = Depends(get_chat_service),
) -> list[ChatRoomSchema]:
    chats = await chat_service.get_my_chats(user_id, filters)
    return chats


@router.post("/create_chat")
async def create_chat(
        chat_create_data: ChatCreateSchema,
        chat_service: ChatServiceInterface = Depends(get_chat_service),
        ws_manager: WSManagerInterface = Depends(get_ws_manager),
) -> ChatRoomSchema:
    chat = await chat_service.create_chat(chat_create_data)
    users = (chat.user1_id, chat.user2_id)
    await ws_manager.send_chat(users, chat)
    return chat


@router.get("/{chat_id}")
async def get_messages(
        chat_id: uuid.UUID,
        filters: BaseFilter = Depends(),
        user_id: uuid.UUID = Depends(get_current_user_id),
        chat_service: ChatServiceInterface = Depends(get_chat_service),
) -> list[MessageSchema]:
    chat = await chat_service.get_chat_by_id(chat_id)
    if not chat:
        raise ChatNotFoundException
    chat_users = (chat.user1_id, chat.user2_id)
    if user_id not in chat_users:
        raise ChatAccessForbiddenException
    messages = await chat_service.get_chat_messages(chat_id, filters)
    return messages


@router.websocket("/ws/my")
async def connect_to_chats(
        websocket: WebSocket,
        filters: BaseFilter = Depends(),
        ws_manager: WSManagerInterface = Depends(get_ws_manager),
        chat_service: ChatServiceInterface = Depends(get_chat_service),
) -> None:
    token = websocket.headers.get("Authorization")
    user_id = get_current_user_id(token)
    await ws_manager.connect(user_id, websocket)
    chats = await chat_service.get_my_chats(user_id, filters)
    for chat in chats:
        await websocket.send_text(chat.json())
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await ws_manager.disconnect(user_id, websocket)


@router.websocket("/ws/{chat_id}")
async def connect_to_chat_by_id(
        chat_id: uuid.UUID,
        websocket: WebSocket,
        filters: BaseFilter = Depends(),
        ws_manager: WSManagerInterface = Depends(get_ws_manager),
        chat_service: ChatServiceInterface = Depends(get_chat_service),
) -> None:
    token = websocket.headers.get("Authorization")
    user_id = get_current_user_id(token)
    chat = await chat_service.get_chat_by_id(chat_id)
    if not chat:
        raise ChatNotFoundException
    chat_users = (chat.user1_id, chat.user2_id)
    if user_id not in chat_users:
        raise ChatAccessForbiddenException
    await ws_manager.connect(chat_id, websocket)
    messages = await chat_service.get_chat_messages(chat_id, filters)
    for message in messages:
        await websocket.send_text(message.json())
    try:
        while True:
            message = await websocket.receive_text()
            await ws_manager.send_message(chat_id, user_id, message)
    except WebSocketDisconnect:
        await ws_manager.disconnect(chat_id, websocket)
