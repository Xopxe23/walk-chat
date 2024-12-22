import uuid
from typing import AsyncGenerator, Optional, Protocol

from fastapi import Depends

from app.chats.repositories import get_chat_repository
from app.chats.schemas import ChatCreateSchema, ChatRoomOutSchema, ChatRoomSchema


class ChatRepositoryInterface(Protocol):
    async def get_my_chats(self, user_id: uuid.UUID) -> list[ChatRoomSchema]:
        ...

    async def get_chat_by_id(self, chat_id: uuid.UUID) -> Optional[ChatRoomSchema]:
        ...

    async def create_chat(self, chat_data: ChatCreateSchema) -> ChatRoomSchema:
        ...


class ChatService:
    def __init__(
            self,
            chat_repository: ChatRepositoryInterface,
    ):
        self.chat_repository = chat_repository

    async def get_my_chats(self, user_id: uuid.UUID) -> list[ChatRoomSchema]:
        chats = await self.chat_repository.get_my_chats(user_id)
        return chats

    async def get_chat_by_id(self, chat_id: uuid.UUID) -> ChatRoomSchema:
        chat = await self.chat_repository.get_chat_by_id(chat_id)
        return chat

    async def create_chat(self, chat_data: ChatCreateSchema) -> ChatRoomSchema:
        chat = await self.chat_repository.create_chat(chat_data)
        return chat


def get_chat_service(
        chat_repository: ChatRepositoryInterface = Depends(get_chat_repository),
) -> AsyncGenerator[ChatService, None]:
    yield ChatService(
        chat_repository=chat_repository,
    )
