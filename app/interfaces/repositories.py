import uuid
from abc import ABC, abstractmethod
from typing import Optional

from app.filters.base import BaseFilter
from app.schemas.chats import ChatCreateSchema, ChatSchema
from app.schemas.messages import MessageCreateSchema, MessageSchema


class ChatsPostgresRepositoryInterface(ABC):
    @abstractmethod
    async def get_my_chats(self, user_id: uuid.UUID, filters: BaseFilter) -> list[ChatSchema]:
        pass

    @abstractmethod
    async def get_chat_by_id(self, chat_id: uuid.UUID) -> Optional[ChatSchema]:
        pass

    @abstractmethod
    async def create_chat(self, chat_data: ChatCreateSchema) -> ChatSchema:
        pass

    @abstractmethod
    async def create_message(self, message_data: MessageCreateSchema) -> MessageSchema:
        pass

    @abstractmethod
    async def get_chat_messages(self, chat_id: uuid.UUID, filters: BaseFilter) -> list[MessageSchema]:
        pass
