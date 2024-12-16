from fastapi import status

from app.utils import CustomHTTPException


class NotFoundException(CustomHTTPException):
    DETAIL = "Not found"
    STATUS_CODE = status.HTTP_404_NOT_FOUND
