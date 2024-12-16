from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session


class ChatRepository:
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session


def get_chat_repository(session: AsyncSession = Depends(get_async_session)) -> AsyncGenerator[ChatRepository, None]:
    yield ChatRepository(
        session=session,
    )
