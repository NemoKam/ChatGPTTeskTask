"""Файл конфигурации приложения."""
import os
from datetime import timezone

# Блок базовых настроек
# --------------------------------------------------------------------------------
# Режим отладки
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
# --------------------------------------------------------------------------------

# Блок Базы Данных
# --------------------------------------------------------------------------------
# Временная зона базы данных
DATABASE_TIMEZONE = timezone.utc
# Базовые данные для URL базы данных PostgreSQL
BASE_DATABASE_URL = (f"{os.getenv('POSTGRES_USER')}"
                f":{os.getenv('POSTGRES_PASSWORD')}"
                f"@{os.getenv('POSTGRES_HOST')}"
                f":{os.getenv('POSTGRES_PORT')}"
                f"/{os.getenv('POSTGRES_DB')}")
# URL для асинхронного подключения к базе данных для ТЕСТОВ
ASYNC_DATABASE_TEST_URL = "postgresql+asyncpg://" + BASE_DATABASE_URL.split("/")[0] + "/" + str(os.getenv('POSTGRES_TEST_DB'))
# URL для асинхронного подключения к базе данных
ASYNC_DATABASE_URL = "postgresql+asyncpg://" + BASE_DATABASE_URL
# URL для синхронного подключения к базе данных
SYNC_DATABASE_URL = "postgresql://" + BASE_DATABASE_URL
# --------------------------------------------------------------------------------

# Блок настроек JWT
# --------------------------------------------------------------------------------
# Секретный ключ для JWT
JWT_SECRET_KEY = str(os.getenv("JWT_SECRET_KEY"))
# Алгоритм шифрования JWT
JWT_ALGORITHM = str(os.getenv("JWT_ALGORITHM"))
# Время жизни токена доступа
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
# Время жизни токена обновления
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7))
# --------------------------------------------------------------------------------
