from fastapi import APIRouter

from src.auth.routes import auth_router


base_router = APIRouter()

@base_router.get("/health", response_model=dict[str, str], status_code=200)
async def health_check() -> dict[str, str]:
    """Эндпоинт для проверки готовности API."""
    return {"status": "ok"}


base_router.include_router(
    prefix="/auth",
    tags=["auth"],
    router=auth_router,
)
