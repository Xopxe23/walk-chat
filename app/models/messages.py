import datetime
import uuid

from sqlalchemy import TIMESTAMP, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Messages(Base):
    __tablename__ = 'messages'

    message_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('chats.chat_id', ondelete='CASCADE'))
    user_id: Mapped[uuid.UUID]
    message_content: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, server_default=text("NOW()"))
