import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import settings
from src.domain.exceptions import DomainException
from src.presentation.api.v1.routers import (
    auth_router,
    user_router,
    project_router,
    task_router,
    health_router,
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Task Manager API",
    description="REST API for managing projects and tasks",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

_status_code_map: dict[str, int] = {
    "USER_NOT_FOUND": 404,
    "DUPLICATE_EMAIL": 409,
    "INVALID_CREDENTIALS": 401,
    "PROJECT_NOT_FOUND": 404,
    "TASK_NOT_FOUND": 404,
    "NOT_PROJECT_OWNER": 403,
    "NOT_PROJECT_MEMBER": 403,
    "ARCHIVED_PROJECT": 403,
    "TASK_ACCESS_DENIED": 403,
    "INVALID_ASSIGNMENT": 422,
    "CANNOT_ASSIGN_TASK": 403,
    "CANNOT_REMOVE_OWNER": 403,
}


@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    status_code = _status_code_map.get(exc.code, 400)
    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.message, "code": exc.code},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor", "code": "INTERNAL_ERROR"},
    )


app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(project_router, prefix="/api/v1")
app.include_router(task_router, prefix="/api/v1")



