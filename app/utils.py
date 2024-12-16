import uuid
from typing import Annotated, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import mapped_column

uuid_pk = Annotated[uuid.UUID, mapped_column(primary_key=True, default=uuid.uuid4)]  # UUID для Base models


class CustomHTTPException(HTTPException):
    """Кастомный exception для наследования"""

    STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR
    DETAIL = "Server error"

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        super().__init__(status_code=self.STATUS_CODE, detail=self.DETAIL, **kwargs)
