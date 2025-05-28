"""Файл сервиса пользователей.

Содежрит в себе как работу с базой так и с внешними функциями.
"""
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any

import jwt
from argon2 import PasswordHasher
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.config import DATABASE_TIMEZONE, JWT_SECRET_KEY, JWT_ALGORITHM, \
    ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES
from core.errors import ErrorWithStatus
from database.models.users import User
from schemas.users import TokenSchema


class UserService:
    """Сервис пользователей.
    
    Args:
        db (AsyncSession): Сессия базы данных.
    """

    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db
    
    def hash_password(self, password: str) -> str:
        """Хеширование пароля.

        Args:
            password (str): Пароль.

        Returns:
            str: Хэш пароля.
        """
        return PasswordHasher().hash(password)


    def verify_password(self, password: str, password_hash: str) -> bool:
        """Проверка пароля.

        Args:
            password (str): Пароль.
            password_hash (str): Хеш пароля.

        Returns:
            bool: True, если пароль совпадает с хешем, иначе вызовет ошибку.
        """
        return PasswordHasher().verify(password_hash, password)


    def check_password_strength(self, password: str) -> bool:
        """Проверка силы пароля.

        Args:
            password (str): Пароль.

        Returns:
            bool: True, если пароль соответствует требованиям.

        Raises:
            ErrorWithStatus[422]: Если длина пароля меньше 8 символов.
        """
        if len(password) < 8:
            raise ErrorWithStatus("Пароль должен состоять минимум из 8 символов.", 422)

        return True


    def generate_token(self, user_id: int) -> TokenSchema:
        """Генерация JWT токена.

        Args:
            user_id (int): ID пользователя.

        Returns:
            TokenSchema: JWT токен с access и refresh токенами.
        """

        access_token_expiration = datetime.now(DATABASE_TIMEZONE) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expiration = datetime.now(DATABASE_TIMEZONE) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

        access_token = jwt.encode(  # type: ignore
            {"user_id": user_id, "exp": access_token_expiration},
            JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM,
        )

        refresh_token = jwt.encode(  # type: ignore
            {"user_id": user_id, "exp": refresh_token_expiration},
            JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM,
        )

        return TokenSchema(
            access_token=access_token,
            access_token_expires_at=access_token_expiration,
            refresh_token=refresh_token,
            refresh_token_expires_at=refresh_token_expiration,
            token_type="Bearer",
        )


    async def get_user_by_email(self, email: str) -> User | None:
        """Получение пользователя по email.

        Args:
            email (str): Email пользователя.

        Returns:
            User | None: Объект пользователя или None, если пользователь не найден.
        """
        user: User | None = (await self.db.execute(
            select(User).where(User.email == email)
        )).scalars().first()
        
        return user


    async def create_user(self, email: str, password: str) -> User:
        """Создание пользователя.

        Args:
            email (str): Email пользователя.
            password (str): Пароль пользователя.

        Returns:
            User: Созданный объект пользователя.

        Raises:
            ErrorWithStatus: Если email некорректен (422).
            ErrorWithStatus: Если пользователь с таким email уже существует (409).
            ErrorWithStatus: Если пароль не соответствует требованиям (422).
        """
        # Проверка валидности email
        if "@" not in email or "." not in email.split("@")[-1]:
            raise ErrorWithStatus("Некорректный email", 422)

        # Проверка существования пользователя с таким email
        existings_user: User | None = await self.get_user_by_email(email)
        if existings_user:
            raise ErrorWithStatus("Пользователь с таким email уже существует", 409)
        
        # Проверка пароля
        self.check_password_strength(password)

        password_hash: str = self.hash_password(password)

        user = User(email=email, password_hash=password_hash)
        self.db.add(user)

        await self.db.commit()
        await self.db.refresh(user)
        
        return user


    def get_user_id_from_access_token(self, token: str) -> int:
        """Проверка JWT токена.

        Args:
            token (str): JWT токен.

        Returns:
            int: ID пользователя, извлеченный из токена.

        Raises:
            ErrorWithStatus: Если токен недействителен (422).
            ErrorWithStatus: Если срок действия токена истек (422).
        """
        data: Any = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])  # type: ignore

        if type(data) is not dict[str, Any] or "user_id" not in data or "exp" not in data:
            raise ErrorWithStatus("Неверный токен", 422)

        if datetime.now(DATABASE_TIMEZONE) > datetime.fromtimestamp(data["exp"], tz=DATABASE_TIMEZONE):
            raise ErrorWithStatus("Срок действия токена истек", 422)

        return data["user_id"]


@lru_cache
def get_user_service(db: AsyncSession) -> UserService:
    """Получение экземпляра сервиса пользователей.

    Args:
        db (AsyncSession): Сессия базы данных.

    Returns:
        UserService: Экземпляр сервиса пользователей.
    """
    return UserService(db)
