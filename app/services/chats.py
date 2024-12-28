import logging
import uuid

from app.brokers.producer import get_kafka_producer
from app.filters.base import BaseFilter
from app.interfaces.brokers import KafkaProducerInterface
from app.interfaces.repositories import ChatsPostgresRepositoryInterface
from app.interfaces.services import ChatsServiceInterface
from app.logger import get_logger
from app.repositories.postgres import get_chats_pg_repository
from app.schemas.chats import ChatCreateSchema, ChatSchema
from app.schemas.messages import MessageCreateSchema, MessageSchema


class ChatsService(ChatsServiceInterface):
    def __init__(
            self,
            chats_pg_repository: ChatsPostgresRepositoryInterface,
            kafka_producer: KafkaProducerInterface,
            logger: logging.Logger,
    ):
        self.chats_pg_repository = chats_pg_repository
        self.kafka_producer = kafka_producer
        self.logger = logger

    async def get_my_chats(self, user_id: uuid.UUID, filters: BaseFilter) -> list[ChatSchema]:
        chats = await self.chats_pg_repository.get_my_chats(user_id, filters)
        return chats

    async def get_chat_by_id(self, chat_id: uuid.UUID) -> ChatSchema:
        chat = await self.chats_pg_repository.get_chat_by_id(chat_id)
        return chat

    async def create_chat(self, chat_data: ChatCreateSchema) -> ChatSchema:
        chat = await self.chats_pg_repository.create_chat(chat_data)
        return chat

    async def get_chat_messages(self, chat_id: uuid.UUID, filters: BaseFilter) -> list[MessageSchema]:
        messages = await self.chats_pg_repository.get_chat_messages(chat_id, filters)
        return messages

    async def create_message(self, message_data: MessageCreateSchema) -> MessageSchema:
        message = await self.chats_pg_repository.create_message(message_data)
        return message


def get_chats_service() -> ChatsService:
    chats_pg_repository = get_chats_pg_repository()
    kafka_producer = get_kafka_producer()
    logger = get_logger()

    return ChatsService(
        chats_pg_repository=chats_pg_repository,
        kafka_producer=kafka_producer,
        logger=logger,
    )
