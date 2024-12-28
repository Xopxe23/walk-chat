from app.services.chats import ChatsService
from tests.dependencies.brokers import get_mocked_kafka_producer
from tests.dependencies.logger import get_mocked_logger
from tests.dependencies.repositories import get_test_chats_pg_repository


async def get_test_chats_service() -> ChatsService:
    chats_pg_repository = get_test_chats_pg_repository()
    kafka_producer = get_mocked_kafka_producer()
    logger = get_mocked_logger()

    return ChatsService(
        chats_pg_repository=chats_pg_repository,
        kafka_producer=kafka_producer,
        logger=logger,
    )
