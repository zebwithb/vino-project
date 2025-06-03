from fastapi import FastAPI

from .core.config import settings
from .endpoints import health, text

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

app.include_router(text.router)
app.include_router(health.router)