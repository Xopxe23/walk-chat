import datetime
import uuid

from pydantic import BaseModel


class MessageCreateSchema(BaseModel):
    chat_id: uuid.UUID
    user_id: uuid.UUID
    message_content: str


class MessageSchema(BaseModel):
    chat_id: uuid.UUID
    user_id: uuid.UUID
    message_content: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True
