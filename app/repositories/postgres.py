import uuid
from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database import get_async_session_maker
from app.exceptions.chat import ChatExistsException
from app.filters.base import BaseFilter
from app.interfaces.repositories import ChatsPostgresRepositoryInterface
from app.models.chats import Chats
from app.models.messages import Messages
from app.schemas.chats import ChatCreateSchema, ChatSchema
from app.schemas.messages import MessageCreateSchema, MessageSchema


class ChatsPostgresRepository(ChatsPostgresRepositoryInterface):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        self.session_maker = session_maker
        self.chat_table = Chats
        self.message_table = Messages

    async def get_my_chats(self, user_id: uuid.UUID, filters: BaseFilter) -> list[ChatSchema]:
        query = (
            select(self.chat_table)
            .where(or_(self.chat_table.user1_id == user_id, self.chat_table.user2_id == user_id))
            .offset(filters.offset)
            .limit(filters.limit)
        )
        async with self.session_maker() as session:
            chats_data = await session.execute(query)
        chats = [ChatSchema.model_validate(chat) for chat in chats_data.scalars()]
        return chats

    async def get_chat_by_id(self, chat_id: uuid.UUID) -> Optional[ChatSchema]:
        query = select(self.chat_table).where(self.chat_table.chat_id == chat_id)
        async with self.session_maker() as session:
            chat_data = await session.execute(query)
        chat = chat_data.scalar_one_or_none()
        return ChatSchema.model_validate(chat) if chat else None

    async def create_chat(self, chat_data: ChatCreateSchema) -> ChatSchema:
        chat = self.chat_table(
            **chat_data.dict()
        )
        async with self.session_maker() as session:
            try:
                session.add(chat)
                await session.commit()
            except IntegrityError:
                raise ChatExistsException
            await session.refresh(chat)
        return ChatSchema.model_validate(chat)

    async def create_message(self, message_data: MessageCreateSchema) -> MessageSchema:
        message = self.message_table(
            **message_data.dict()
        )
        async with self.session_maker() as session:
            session.add(message)
            await session.commit()
            await session.refresh(message)
        return MessageSchema.model_validate(message)

    async def get_chat_messages(self, chat_id: uuid.UUID, filters: BaseFilter) -> list[MessageSchema]:
        query = (
            select(self.message_table)
            .where(self.message_table.chat_id == chat_id)
            .order_by(self.message_table.created_at.desc())
            .offset(filters.offset)
            .limit(filters.limit)
        )
        async with self.session_maker() as session:
            result = await session.execute(query)
        messages = [MessageSchema.model_validate(message) for message in result.scalars()]
        return messages


def get_chats_pg_repository() -> ChatsPostgresRepository:
    session_maker = get_async_session_maker()
    return ChatsPostgresRepository(
        session_maker=session_maker,
    )
