from fastapi import status

from app.utils import CustomHTTPException


class InvalidTokenException(CustomHTTPException):
    STATUS_CODE = status.HTTP_401_UNAUTHORIZED
    DETAIL = "Token is not valid"

    def __init__(self) -> None:
        super().__init__(headers={"WWW-Authenticate": "Bearer"})
