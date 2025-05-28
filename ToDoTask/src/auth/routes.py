"""Файл методов аутентификации."""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession


from database.database import get_db
from database.models.users import User

from schemas.users import RegisterUserRequestSchema, LoginUserRequestSchema, \
                          RegisterUserResponseSchema

from services.users import get_user_service
from schemas.users import TokenSchema
from core.logger import logger
from core.errors import ErrorWithStatus


auth_router = APIRouter()


@auth_router.post("/register", response_model=RegisterUserResponseSchema, status_code=201)
async def register(register_user_data: RegisterUserRequestSchema,
                   db: Any = Depends(get_db)
) -> RegisterUserResponseSchema:
    """
    Регистрация нового пользователя.

    Args:
        register_user_data (RegisterUserRequestSchema): Данные для регистрации пользователя.
        db (AsyncSession): Сессия базы данных.

    Returns:
        RegisterUserResponseSchema: Зарегистрированный пользователь.

    Raises:
        HTTPException: Если email некорректен (422).
        HTTPException: Если пользователь с таким email уже существует (409).
        HTTPException: Если пароль не соответствует требованиям (422).
    """
    user_service = get_user_service(db)

    try:
        user: User = await user_service.create_user(register_user_data.email, register_user_data.password)
    except ErrorWithStatus as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

    return RegisterUserResponseSchema.model_validate(user)


@auth_router.post("/login", response_model=TokenSchema, status_code=200)
async def login(login_user_data: LoginUserRequestSchema,
                db: AsyncSession = Depends(get_db)
) -> TokenSchema:
    """
    Аутентификация пользователя.

    Args:
        login_user_data (LoginUserRequestSchema): Данные для аутентификации пользователя.
        db (AsyncSession): Сессия базы данных.

    Returns:
        TokenSchema: JWT токен для аутентифицированного пользователя.

    Raises:
        HTTPException: Если пользователь с указанным email не найден (400).
        HTTPException: Если пароль неверный (400).
    """
    user_service = get_user_service(db)

    # Проверяем, существует ли пользователь с таким email
    user: User | None = await user_service.get_user_by_email(login_user_data.email)
    if not user:
        raise HTTPException(status_code=400, detail="Пользователь не найден")
    
    # Проверяем, совпадают ли пароли
    if not user_service.verify_password(login_user_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Неверный пароль")

    # Генерируем JWT токен
    token: TokenSchema = user_service.generate_token(user.id)
    
    return token
