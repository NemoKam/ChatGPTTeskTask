"""Тестирование регистрации пользователя."""
import pytest
from httpx import AsyncClient

from database.models.users import User


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("test_user_email, test_user_password", [
    ("first_user@localhost.com", "S5P3RS3CR3TP4SSW0RD"),
    ("second_user@ok.com", "12345678"),
    ("third_user@super.ru", "OKOKOKOK12"),
])
async def test_register_first_user(
    unauthorized_client: AsyncClient,
    test_user_email: str,
    test_user_password: str,
):
    """Тестирование регистрации пользователя."""

    # Регистрация нового пользователя
    response = await unauthorized_client.post(
        "/auth/register",
        json={
            "email": test_user_email,
            "password": test_user_password,
        }
    )
    response_json = response.json()

    assert response.status_code == 201
    assert all(field in response_json for field in ("id", "email",))
    assert response_json["email"] == test_user_email


@pytest.mark.asyncio(loop_scope="session")
async def test_register_user_already_exists(
    unauthorized_client: AsyncClient,
    first_example_user: User
):
    """
    Тестирование регистрации пользователя с уже существующим email.
    """

    # Попытка регистрации пользователя с уже существующим email
    response = await unauthorized_client.post(
        "/auth/register",
        json={
            "email": first_example_user.email,
            "password": "AnyPassword",
        }
    )
    assert response.status_code == 409
    assert response.json() == {
        "detail": "Пользователь с таким email уже существует"
    }


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("test_user_email, test_user_password", [
    ("invalid_email", "test_register_password"),
    ("invalid_email@com", "OKOKOKOK12"),
    ("invalid_email.com", "12345678"),
])
async def test_register_user_invalid_email(
    unauthorized_client: AsyncClient,
    test_user_email: str,
    test_user_password: str
):
    """
    Тестирование регистрации пользователя с невалидным email.
    """

    # Попытка регистрации пользователя с невалидным email
    response = await unauthorized_client.post(
        "/auth/register",
        json={
            "email": test_user_email,
            "password": test_user_password,
        }
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Некорректный email"
    }


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("test_user_email, test_user_password", [
    ("invalid_password@localhost.com", None),
    ("invalid_password@localhost.com", "12333"),
    ("invalid_password@localhost.com", ""),
])
async def test_register_user_invalid_password(
    unauthorized_client: AsyncClient,
    test_user_email: str,
    test_user_password: str | None
):
    """
    Тестирование регистрации пользователя с невалидным паролем.
    """

    # Попытка регистрации пользователя без пароля
    response = await unauthorized_client.post(
        "/auth/register",
        json={
            "email": test_user_email,
        }
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": "'password' Field required"
    }

    # Попытка регистрации пользователя с паролем менее 8 символов
    response = await unauthorized_client.post(
        "/auth/register",
        json={
            "email": test_user_email,
            "password": test_user_password,
        }
    )
    assert response.status_code == 422

    if test_user_password is None:
        assert response.json() == {
            "detail": "'password' Input should be a valid string"
        }
    else:
        # Если пароль не None, то он должен быть менее 8 символов
        assert response.json() == {
            "detail": "Пароль должен состоять минимум из 8 символов."
        }
