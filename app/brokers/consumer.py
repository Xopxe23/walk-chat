import json
import logging
from typing import AsyncGenerator, Optional

from aiokafka import AIOKafkaConsumer, ConsumerRecord
from aiokafka.errors import KafkaError

from app.configs.main import settings
from app.interfaces.managers import ConnectionsManagerInterface
from app.interfaces.services import ChatsServiceInterface
from app.logger import get_logger
from app.managers.connections import get_ws_manager
from app.schemas.chats import ChatCreateSchema
from app.services.chats import get_chats_service


class KafkaConsumer:
    _instance: Optional["KafkaConsumer"] = None

    def __new__(cls, kafka_url: str, group_id: str, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
            self,
            kafka_url: str,
            group_id: str,
            chats_service: ChatsServiceInterface,
            ws_manager: ConnectionsManagerInterface,
            logger: logging.Logger,
    ):
        if not hasattr(self, 'consumer'):
            self.consumer = AIOKafkaConsumer(
                bootstrap_servers=kafka_url,
                group_id=group_id,
                enable_auto_commit=True
            )
            self.chats_service = chats_service
            self.ws_manager = ws_manager
            self.logger = logger
            self.subscribed_topics = []

    async def start(self) -> None:
        await self.consumer.start()

    async def stop(self) -> None:
        if self.consumer:
            await self.consumer.stop()
            self.consumer = None

    async def subscribe(self, topics: list[str]) -> None:
        self.subscribed_topics.extend(topics)
        self.consumer.subscribe(topics)

    async def consume_messages(self) -> AsyncGenerator[ConsumerRecord, None]:
        """Consume messages from subscribed topics."""
        try:
            async for message in self.consumer:
                yield message
        except (KafkaError, json.JSONDecodeError, UnicodeDecodeError) as e:
            self.logger.error(f"Error while consuming messages: {e}")

    async def process_messages(self) -> None:
        """Обрабатываем сообщения из Kafka."""
        async for message in self.consume_messages():
            if message.topic == "matches":
                data = self._decode_message(message)
                chat_data = ChatCreateSchema(
                    user1_id=data["user1_id"],
                    user2_id=data["user2_id"],
                )
                chat = await self.chats_service.create_chat(chat_data)
                await self.ws_manager.send_chat(chat)

    def _decode_message(self, message: ConsumerRecord) -> dict:
        try:
            data = json.loads(message.value.decode("utf-8"))
            self.logger.info(f"Received message from topic {message.topic}: {data}")
            return data
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON: {e} | Raw message: {message.value}")


def get_kafka_consumer() -> KafkaConsumer:
    chats_service = get_chats_service()
    logger = get_logger()
    ws_manager = get_ws_manager()

    return KafkaConsumer(
        kafka_url=settings.kafka.KAFKA_URL,
        group_id="chats",
        chats_service=chats_service,
        ws_manager=ws_manager,
        logger=logger,
    )
