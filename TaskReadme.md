Описание задания
Разработать REST-сервис «Todo-приложение» с возможностью:

регистрации и аутентификации пользователей,

создания, чтения, обновления и удаления задач (CRUD),

фильтрации и постраничной выдачи списка задач.

Сервис должен быть упакован в Docker и сопровождаться наборами автоматизированных тестов и документацией.

Требования к функционалу
Модели и БД

User (id, email, password_hash, created_at)

TodoItem (id, owner_id → User.id, title, description, is_done (bool), due_date (optional), created_at, updated_at)

Использовать PostgreSQL (можно SQLite для простоты, но предпочтительнее PostgreSQL).

API-эндпоинты (JSON)

POST /auth/register — регистрация (email + пароль)

POST /auth/login — получение JWT-токена

GET /todos — список задач пользователя (+ фильтрация по is_done=true|false, due_date; параметр page, limit)

POST /todos — создание задачи

GET /todos/{id} — получение конкретной задачи

PUT /todos/{id} — полное обновление

PATCH /todos/{id} — частичное обновление (например, только поле is_done)

DELETE /todos/{id} — удаление задачи

Аутентификация и авторизация

JWT-токен, передаётся в заголовке Authorization: Bearer <token>.

Доступ к эндпоинтам /todos* только для аутентифицированных.

Документация

Swagger/OpenAPI (например, через FastAPI или flask-restx).

Тесты

Unit- и интеграционные тесты (pytest, тестовая база).

Проверить основные сценарии: регистрация, логин, CRUD-операции, доступ без токена.

Дополнительные фичи (опционально, за плюс к оценке)

Кэширование списка задач (Redis).

Логирование запросов (например, structlog).

CI-pipeline (GitHub Actions).

Технические требования
Язык: Python ≥3.9

Фреймворк: FastAPI или Flask (+ Flask-RESTful/Flask-RESTX)

ORM: SQLAlchemy, или Tortoise ORM (для FastAPI)

Docker — Dockerfile + docker-compose для БД и самого сервиса

Формат кода: PEP8 (использовать flake8/isort)

В README:

инструкции по запуску (локально и через Docker)

примеры запросов (curl или HTTPie)

описание структуры проекта
