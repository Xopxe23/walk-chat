from fastapi import status

from app.exceptions.common import NotFoundException
from app.utils import CustomHTTPException


class ChatAccessForbiddenException(CustomHTTPException):
    STATUS_CODE = status.HTTP_403_FORBIDDEN
    DETAIL = "User is not in chat"


class ChatNotFoundException(NotFoundException):
    DETAIL = "Chat not found"


class ChatExistsException(CustomHTTPException):
    STATUS_CODE = status.HTTP_409_CONFLICT
    DETAIL = "Chat already exists"
