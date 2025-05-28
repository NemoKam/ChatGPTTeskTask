from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.config import DATABASE_TIMEZONE


class DefaultBase(DeclarativeBase):
    pass


class ExtendedBase(DefaultBase):
    """Расширенная базовая модель."""
    __abstract__ = True
    __tablename__ = "base"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(DATABASE_TIMEZONE), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(DATABASE_TIMEZONE), onupdate=lambda: datetime.now(DATABASE_TIMEZONE), nullable=False)
