"""Конфигурационный файл для тестов."""
from typing import AsyncGenerator

import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, \
                                    AsyncConnection, AsyncSession, AsyncTransaction


from core.config import ASYNC_DATABASE_TEST_URL
from database.database import get_db
from database.models.base import DefaultBase
from database.models.users import User 
from services.users import get_user_service
from fast import app


# ----------------------------------------------------------------------
# Конфигурация тестовой базы данных для FAST API сервера

@pytest_asyncio.fixture(scope="session", autouse=True)
async def async_engine() -> AsyncGenerator[AsyncEngine, None]:
    yield create_async_engine(ASYNC_DATABASE_TEST_URL, echo=False, future=True)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def async_session_local(
    async_engine: AsyncEngine
) -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    yield async_sessionmaker(autocommit=False, autoflush=False, bind=async_engine)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database(async_engine: AsyncEngine):
    async with async_engine.begin() as conn:
        await conn.run_sync(DefaultBase.metadata.drop_all)
        await conn.run_sync(DefaultBase.metadata.create_all)

    yield

    # async with async_engine.begin() as conn:
        # await conn.run_sync(DefaultBase.metadata.drop_all)


# Функциия для получения асинрхонной сессии к тестовой базе данных
@pytest_asyncio.fixture(scope="session", autouse=True)
async def override_get_db(async_session_local: async_sessionmaker[AsyncSession]):
    # Причина вложенности кроется в ошибке, возникающей из-за аннотации.
    # Нельзя овверайдить функцию с переданным аргументов, аннотация которого = async_sessionmaker[AsyncSession]
    # Так как async_sessionmaker[AsyncSession] is not a valid Pydantic Field
    async def _get_test_db():
        async with async_session_local() as db:
            yield db
    app.dependency_overrides[get_db] = _get_test_db

# ----------------------------------------------------------------------


# Фикстура для подключения к базе данных
@pytest_asyncio.fixture(scope="session")
async def connection(async_engine: AsyncEngine) -> AsyncGenerator[AsyncConnection, None]:
    async with async_engine.connect() as connection:
        yield connection


@pytest_asyncio.fixture(scope="session")
async def transaction(
    connection: AsyncConnection,
) -> AsyncGenerator[AsyncTransaction, None]:
    async with connection.begin() as transaction:
        yield transaction


# Фикстура для создания асинхронной сессии базы данных,
# которая будет держать базу чистой между тестами
@pytest_asyncio.fixture(scope="session")
async def session(
    connection: AsyncConnection, transaction: AsyncTransaction
) -> AsyncGenerator[AsyncSession, None]:
    """Фикстура для создания асинхронной сессии базы данных."""
    async_session = AsyncSession(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )
    try:
        yield async_session
    finally:
        await async_session.close()
        await transaction.rollback()
        await connection.close()


@pytest_asyncio.fixture(scope="session")
async def session_no_rollback(connection: AsyncConnection) -> AsyncGenerator[AsyncSession, None]:
    """Фикстура для создания асинхронной сессии базы данных без отката транзакции."""
    async_session = AsyncSession(bind=connection)
    try:
        yield async_session
    finally:
        await async_session.close()


# Фикстура пустого клиента для тестов
@pytest_asyncio.fixture(scope="session")
async def base_client() -> AsyncGenerator[AsyncClient, None]:
    """Возвращает AsyncClient модель"""
    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app),
                        base_url="http://127.0.0.1:8000",
                        headers={"Content-Type": "application/json"}) as client:
            yield client


@pytest_asyncio.fixture(scope="session")
async def unauthorized_client(base_client: AsyncClient) -> AsyncGenerator[AsyncClient, None]:
    """Возвращает AsyncClient, подключённый к приложению FastAPI."""
    yield base_client


# Первый тестовый пользователь
@pytest_asyncio.fixture(scope="session")
async def first_example_user(session_no_rollback: AsyncSession) -> User:
    """Ввращает первого тестового пользователя."""
    
    first_example_user_email = "first_example_user@localhost.com"

    user_service = get_user_service(session_no_rollback)

    existing_first_example_user: User | None = await user_service.get_user_by_email(first_example_user_email)

    if existing_first_example_user is not None:
        return existing_first_example_user

    return await user_service.create_user(
        email=first_example_user_email,
        password="SuperSecretPassword1234",
    )


# Асинхронный тестовый клиент для первого тестового авторизованного пользователя
@pytest_asyncio.fixture(scope="session")
async def first_example_user_client(
    unauthorized_client: AsyncClient,
    base_client: AsyncClient,
) -> AsyncGenerator[AsyncClient, None]:
    """Возвращает AsyncClient первого пользователя."""

    # Вход первого пользователя
    response = await unauthorized_client.post(
        "/auth/login",
        json={
            "email": "first_example_user@localhost.com",
            "password": "SuperSecretPassword1234",
        },
    )

    authorized_client = base_client
    authorized_client.headers["Authorization"] = f"Bearer {response.json()['access_token']}"

    yield authorized_client
