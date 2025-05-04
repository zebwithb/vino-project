import time

from fastapi import APIRouter

from ..schemas.text import HealthResponse

router = APIRouter(tags=["health"])
start_time = time.time()

@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        uptime=time.time() - start_time
    )