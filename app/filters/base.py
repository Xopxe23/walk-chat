from pydantic import BaseModel


class BaseFilter(BaseModel):
    limit: int = 30
    offset: int = 0
