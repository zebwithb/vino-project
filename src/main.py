import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .app.services.text_analysis import find_most_similar, generate_summary

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

@app.post("/v1/summarize", response_model=SummarizeResponse)
async def summarize(request: SummarizeRequest):
    try:
        summary_text = await generate_summary(request.text)
        return SummarizeResponse(summary=summary_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.post("/v1/similarity", response_model=SimilarityResponse)
async def similarity(request: SimilarityRequest):
    try:
        closest_text, max_similarity = await find_most_similar(request.query, request.texts)
        return SimilarityResponse(
            closest_text=closest_text,
            score=max_similarity
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        uptime=time.time() - start_time
    )