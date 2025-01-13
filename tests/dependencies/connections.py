from app.managers.connections import ConnectionManager
from tests.dependencies.services import get_test_chats_service


async def get_test_ws_manager() -> ConnectionManager:
    chats_service = get_test_chats_service()
    return ConnectionManager(
        chats_service=chats_service,
    )
