import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()
start_time = time.time()

class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=1)

class SummarizeResponse(BaseModel):
    summary: str

class SimilarityRequest(BaseModel):
    query: str = Field(..., min_length=1)
    texts: list[str] = Field(..., min_length=1)

class SimilarityResponse(BaseModel):
    closest_text: str
    score: float = Field(..., ge=0, le=1)

class HealthResponse(BaseModel):
    status: str
    uptime: float

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        uptime=time.time() - start_time
    )
    