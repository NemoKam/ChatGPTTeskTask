"""Тестирование здоровья приложения."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(unauthorized_client: AsyncClient):
    """
    Тестирование эндпоинта /health.
    """
    response = await unauthorized_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

