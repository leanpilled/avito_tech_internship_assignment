import uuid

from sqlalchemy.orm import Mapped, mapped_column
from data.db.connection.session import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    balance: Mapped[int] = mapped_column(nullable=False)
