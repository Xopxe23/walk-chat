import uuid
from typing import AsyncGenerator, Optional

from fastapi import Depends
from sqlalchemy import or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.chats.filters import BaseFilter
from app.chats.models import ChatMessage, ChatRoom
from app.chats.schemas import ChatCreateSchema, ChatRoomOutSchema, ChatRoomSchema, MessageCreateSchema, MessageSchema
from app.database import get_async_session


class ChatRepository:
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.chat_table = ChatRoom
        self.message_table = ChatMessage

    async def get_my_chats(self, user_id: uuid.UUID) -> list[ChatRoomSchema]:
        query = select(self.chat_table).where(or_(
            self.chat_table.user1_id == user_id,
            self.chat_table.user2_id == user_id,
        ))
        chats_data = await self.session.execute(query)
        chats = [ChatRoomSchema.model_validate(chat) for chat in chats_data.scalars()]
        return chats

    async def get_chat_by_id(self, chat_id: uuid.UUID) -> Optional[ChatRoomSchema]:
        query = select(self.chat_table).where(self.chat_table.chat_id == chat_id)
        chat_data = await self.session.execute(query)
        chat = chat_data.scalar_one_or_none()
        return ChatRoomSchema.model_validate(chat) if chat else None

    async def create_chat(self, chat_data: ChatCreateSchema) -> ChatRoomSchema:
        chat = self.chat_table(
            **chat_data.dict()
        )
        self.session.add(chat)
        await self.session.commit()
        await self.session.refresh(chat)
        return ChatRoomSchema.model_validate(chat)

    async def create_message(self, message_data: MessageCreateSchema) -> MessageSchema:
        message = self.message_table(
            **message_data.dict()
        )
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return MessageSchema.model_validate(message)

    async def get_chat_messages(self, chat_id: uuid.UUID, filters: BaseFilter) -> list[MessageSchema]:
        query = (
            select(
                self.message_table,
                func.count(self.message_table.message_id).over().label("total_count")
            )
            .where(self.message_table.chat_id == chat_id)
            .order_by(self.message_table.created_at.desc())
            .offset(filters.offset)
            .limit(filters.limit)
        )
        result = await self.session.execute(query)
        messages = [MessageSchema.model_validate(message) for message in result.scalars()]
        return messages


def get_chat_repository(session: AsyncSession = Depends(get_async_session)) -> AsyncGenerator[ChatRepository, None]:
    yield ChatRepository(
        session=session,
    )
