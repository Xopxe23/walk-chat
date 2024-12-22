import datetime
import uuid

from pydantic import BaseModel


class UserSchema(BaseModel):
    user_id: uuid.UUID
    name: str


class ChatCreateSchema(BaseModel):
    user1_id: uuid.UUID
    user2_id: uuid.UUID


class ChatRoomSchema(BaseModel):
    chat_id: uuid.UUID
    user1_id: uuid.UUID
    user2_id: uuid.UUID
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class ChatRoomOutSchema(BaseModel):
    chat_id: uuid.UUID
    interlocutor_id: uuid.UUID
    last_message: str
    last_message_sender: str
    last_message_time: datetime.datetime


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
