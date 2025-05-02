from fastapi import FastAPI
from .core.config import settings
from .routers import text, health

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

app.include_router(text.router)
app.include_router(health.router)