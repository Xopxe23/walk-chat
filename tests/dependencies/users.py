import uuid

from fastapi import Depends

from app.exceptions.auth import InvalidTokenException
from app.utils import api_key_header


async def mock_get_current_user_id(token: str = Depends(api_key_header)) -> uuid.UUID:
    if token:
        user_id = "9c92aabb-3771-4756-97cc-b781371ff19a"
        return uuid.UUID(user_id)
    raise InvalidTokenException
