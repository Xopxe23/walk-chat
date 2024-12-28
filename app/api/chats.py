import uuid

from fastapi import APIRouter, Depends
from fastapi.websockets import WebSocket, WebSocketDisconnect

from app.exceptions.chat import ChatAccessForbiddenException, ChatNotFoundException
from app.filters.base import BaseFilter
from app.interfaces.managers import ConnectionsManagerInterface
from app.interfaces.services import ChatsServiceInterface
from app.managers.connections import get_ws_manager
from app.schemas.chats import ChatCreateSchema, ChatSchema
from app.schemas.messages import MessageSchema
from app.services.chats import get_chats_service
from app.utils import get_current_user_id

router = APIRouter(
    prefix="/chats",
    tags=["Chats"]
)


@router.get("/my")
async def get_my_chats(
        user_id: uuid.UUID = Depends(get_current_user_id),
        filters: BaseFilter = Depends(),
        chats_service: ChatsServiceInterface = Depends(get_chats_service),
) -> list[ChatSchema]:
    chats = await chats_service.get_my_chats(user_id, filters)
    return chats


@router.post("/create_chat")
async def create_chat(
        chat_create_data: ChatCreateSchema,
        chats_service: ChatsServiceInterface = Depends(get_chats_service),
        ws_manager: ConnectionsManagerInterface = Depends(get_ws_manager),
) -> ChatSchema:
    chat = await chats_service.create_chat(chat_create_data)
    users = (str(chat.user1_id), str(chat.user2_id))
    await ws_manager.send_chat(users, chat)
    return chat


@router.websocket("/ws/my")
async def get_my_chats_ws(
        websocket: WebSocket,
        filters: BaseFilter = Depends(),
        ws_manager: ConnectionsManagerInterface = Depends(get_ws_manager),
        chats_service: ChatsServiceInterface = Depends(get_chats_service),
) -> None:
    token = websocket.headers.get("Authorization")
    user_id = get_current_user_id(token)
    await ws_manager.connect(user_id, websocket)
    chats = await chats_service.get_my_chats(user_id, filters)
    for chat in chats:
        await websocket.send_text(chat.json())
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await ws_manager.disconnect(user_id, websocket)


@router.get("/{chat_id}")
async def get_messages(
        chat_id: uuid.UUID,
        filters: BaseFilter = Depends(),
        user_id: uuid.UUID = Depends(get_current_user_id),
        chat_service: ChatsServiceInterface = Depends(get_chats_service),
) -> list[MessageSchema]:
    chat = await chat_service.get_chat_by_id(chat_id)
    if not chat:
        raise ChatNotFoundException
    chat_users = (chat.user1_id, chat.user2_id)
    if user_id not in chat_users:
        raise ChatAccessForbiddenException
    messages = await chat_service.get_chat_messages(chat_id, filters)
    return messages


@router.websocket("/ws/{chat_id}")
async def connect_to_chat_by_id(
        chat_id: uuid.UUID,
        websocket: WebSocket,
        filters: BaseFilter = Depends(),
        ws_manager: ConnectionsManagerInterface = Depends(get_ws_manager),
        chat_service: ChatsServiceInterface = Depends(get_chats_service),
) -> None:
    token = websocket.headers.get("Authorization")
    user_id = get_current_user_id(token)
    chat = await chat_service.get_chat_by_id(chat_id)
    if not chat:
        raise ChatNotFoundException
    chat_users = (chat.user1_id, chat.user2_id)
    if uuid.UUID(user_id) not in chat_users:
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
