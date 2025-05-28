"""Файл подключения к базе данных."""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, \
                                    AsyncSession, AsyncEngine

from core.config import ASYNC_DATABASE_URL, DEBUG_MODE


engine: AsyncEngine | None = None
AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = None


def init_engine():
    global engine, AsyncSessionLocal
    engine = create_async_engine(ASYNC_DATABASE_URL, echo=DEBUG_MODE, future=True)
    AsyncSessionLocal = async_sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )

# Функциия для получения асинрхонной сессии базы данных
async def get_db() -> AsyncGenerator[AsyncSession]:
    if AsyncSessionLocal is not None:
        db = AsyncSessionLocal()
        try:
            yield db
        finally:
            await db.close()
