from app.managers.connections import ConnectionManager
from tests.dependencies.services import get_test_chats_service


async def get_ws_manager() -> ConnectionManager:
    chats_services = get_test_chats_service()
    return ConnectionManager(
        chats_services=chats_services,
    )
