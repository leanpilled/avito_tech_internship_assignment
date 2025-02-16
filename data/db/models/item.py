import uuid

from sqlalchemy.orm import Mapped, mapped_column

from data.db.connection.session import Base


class ItemModel(Base):
    __tablename__ = "items"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    type: Mapped[str] = mapped_column(nullable=False, unique=True)
    price: Mapped[int] = mapped_column(nullable=False)
