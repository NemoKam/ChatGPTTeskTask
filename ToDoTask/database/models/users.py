from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from database.models.base import ExtendedBase


class User(ExtendedBase):
    """Модель пользователя."""
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
