import uuid

from fastapi.websockets import WebSocket

from app.interfaces.services import ChatsServiceInterface
from app.schemas.chats import ChatSchema
from app.schemas.messages import MessageCreateSchema
from app.services.chats import get_chats_service


class ConnectionManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, chats_service: ChatsServiceInterface):
        if not hasattr(self, 'active_connections'):
            self.active_connections: dict[uuid.UUID, list[WebSocket]] = {}
        self.chats_service = chats_service

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
        message = await self.chats_service.create_message(message_data)
        if chat_id in self.active_connections:
            chat_connections = self.active_connections[chat_id]
            for connection in chat_connections:
                await connection.send_text(message.json())

    async def send_chat(self, chat: ChatSchema):
        active_connections = []
        chat_users = str(chat.user1_id), str(chat.user2_id)
        for user in chat_users:
            if user in self.active_connections:
                active_connections.extend(self.active_connections[user])
        for connection in active_connections:
            await connection.send_text(chat.json())


def get_ws_manager() -> ConnectionManager:
    chats_service = get_chats_service()
    return ConnectionManager(
        chats_service=chats_service,
    )
