import time
from typing import Any, Sequence
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.trustedhost import TrustedHostMiddleware


from database.database import init_engine, engine
from src.routes import base_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_engine()
    yield
    if engine is not None:
        await engine.dispose()


app = FastAPI(lifespan=lifespan)


# Middleware block
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"]
)


# Custom middleware to coune time requests
@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Any) -> Response:
    start_time = time.perf_counter()
    response: Response = await call_next(request)
    process_time: float = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# HTTP Exceptions block
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    errors: Sequence[Any] = exc.errors()

    if len(errors) > 0:
        first_error: Any = errors[0]
        if isinstance(first_error, dict) and all(key in first_error for key in ("msg", "loc")):
            return JSONResponse({"detail": f"'{first_error['loc'][-1]}' {first_error['msg']}"}, status_code=422)

    return JSONResponse({"detail": str(exc)}, status_code=422)

# Router block
app.include_router(
    prefix="",
    tags=["base_router"],
    router=base_router,
)
