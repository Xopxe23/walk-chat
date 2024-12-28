from app.repositories.postgres import ChatsPostgresRepository
from tests.dependencies.database import get_test_session_maker


def get_test_chats_pg_repository() -> ChatsPostgresRepository:
    session_maker = get_test_session_maker()
    return ChatsPostgresRepository(
        session_maker=session_maker,
    )
