import datetime
import uuid

from sqlalchemy import TIMESTAMP, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Chats(Base):
    __tablename__ = 'chats'

    chat_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user1_id: Mapped[uuid.UUID]
    user2_id: Mapped[uuid.UUID]
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, server_default=text("NOW()"))

    __table_args__ = (
        # Добавление уникального индекса на пару (user1_id, user2_id)
        UniqueConstraint('user1_id', 'user2_id', name='uq_user_pair'),
        UniqueConstraint('user2_id', 'user1_id', name='uq_user_pair_reversed')
    )
