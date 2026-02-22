# Routes package
from .auth import router as auth_router
from .reports import router as reports_router
from .templates import router as templates_router
from .schedules import router as schedules_router

__all__ = [
    "auth_router",
    "reports_router",
    "templates_router",
    "schedules_router",
]
