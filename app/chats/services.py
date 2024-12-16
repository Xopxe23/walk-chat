from typing import AsyncGenerator, Protocol

from fastapi import Depends

from app.chats.repositories import get_chat_repository


class ChatRepositoryInterface(Protocol):
    pass


class ChatService:
    def __init__(
            self,
            chat_repository: ChatRepositoryInterface,
    ):
        self.chat_repository = chat_repository


def get_chat_service(
        chat_repository: ChatRepositoryInterface = Depends(get_chat_repository),
) -> AsyncGenerator[ChatService, None]:
    yield ChatService(
        chat_repository=chat_repository,
    )
