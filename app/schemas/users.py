import uuid

from pydantic import BaseModel


class UserSchema(BaseModel):
    user_id: uuid.UUID
    name: str
