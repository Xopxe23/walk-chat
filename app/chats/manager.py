import uuid
from typing import Protocol

from fastapi import Depends, WebSocket

from app.chats.repositories import get_chat_repository
from app.chats.schemas import ChatRoomSchema, MessageCreateSchema, MessageSchema


class ChatRepositoryInterface(Protocol):
    async def create_message(self, message_data: MessageCreateSchema) -> MessageSchema:
        ...


class ConnectionManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, chat_repository: ChatRepositoryInterface):
        if not hasattr(self, 'active_connections'):
            self.active_connections: dict[uuid.UUID, list[WebSocket]] = {}
        self.chat_repository = chat_repository

    async def connect(self, connection_id: uuid.UUID, websocket: WebSocket):
        if connection_id not in self.active_connections:
            self.active_connections[connection_id] = []
        self.active_connections[connection_id].append(websocket)
        await websocket.accept()

    async def disconnect(self, connection_id: uuid.UUID, websocket: WebSocket):
        if connection_id in self.active_connections:
            self.active_connections[connection_id].remove(websocket)
            if not self.active_connections[connection_id]:
                del self.active_connections[connection_id]

    async def send_message(self, chat_id: uuid.UUID, user_id: uuid.UUID, message: str):
        message_data = MessageCreateSchema(
            chat_id=chat_id,
            user_id=user_id,
            message_content=message,
        )
        message = await self.chat_repository.create_message(message_data)
        if chat_id in self.active_connections:
            chat_connections = self.active_connections[chat_id]
            for connection in chat_connections:
                await connection.send_text(message.json())

    async def send_chat(self, user_ids: list[uuid.UUID], new_chat: ChatRoomSchema):
        active_connections = []
        for user in user_ids:
            if user in self.active_connections:
                active_connections.extend(self.active_connections[user])
        for connection in active_connections:
            await connection.send_text(new_chat.json())


async def get_ws_manager(
        chat_repository: ChatRepositoryInterface = Depends(get_chat_repository),
) -> ConnectionManager:
    return ConnectionManager(
        chat_repository=chat_repository,
    )
