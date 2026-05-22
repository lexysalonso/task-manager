from .auth_router import router as auth_router
from .project_router import router as project_router
from .task_router import router as task_router
from .health_router import router as health_router

__all__ = ["auth_router", "project_router", "task_router", "health_router"]
