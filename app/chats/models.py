import datetime
import uuid

from sqlalchemy import ForeignKey, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.utils import uuid_pk


class ChatRoom(Base):
    __tablename__ = 'chat_room'

    chat_id: Mapped[uuid_pk]
    user1_id: Mapped[uuid.UUID]
    user2_id: Mapped[uuid.UUID]
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, server_default=text("NOW()"))

    __table_args__ = (
        # Добавление уникального индекса на пару (user1_id, user2_id)
        UniqueConstraint('user1_id', 'user2_id', name='uq_user_pair'),
        UniqueConstraint('user2_id', 'user1_id', name='uq_user_pair_reversed')
    )


class ChatMessage(Base):
    __tablename__ = 'chat_message'

    message_id: Mapped[uuid_pk]
    chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('chat_room.chat_id', ondelete='CASCADE'))
    user_id: Mapped[uuid.UUID]
    message_content: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, server_default=text("NOW()"))
