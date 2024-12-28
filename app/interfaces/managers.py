import uuid
from abc import ABC, abstractmethod

from fastapi.websockets import WebSocket

from app.schemas.chats import ChatSchema


class ConnectionsManagerInterface(ABC):
    @abstractmethod
    async def connect(self, connection_id: uuid.UUID, websocket: WebSocket):
        pass

    @abstractmethod
    async def disconnect(self, connection_id: uuid.UUID, websocket: WebSocket):
        pass

    @abstractmethod
    async def send_message(self, chat_id: uuid.UUID, user_id: uuid.UUID, message: str):
        pass

    @abstractmethod
    async def send_chat(self, user_ids: list[uuid.UUID], new_chat: ChatSchema):
        pass
