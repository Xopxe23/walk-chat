import datetime
import uuid

from pydantic import BaseModel


class ChatCreateSchema(BaseModel):
    user1_id: uuid.UUID
    user2_id: uuid.UUID


class ChatSchema(BaseModel):
    chat_id: uuid.UUID
    user1_id: uuid.UUID
    user2_id: uuid.UUID
    created_at: datetime.datetime

    class Config:
        from_attributes = True
