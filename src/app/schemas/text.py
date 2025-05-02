from pydantic import BaseModel, Field
from typing import List

class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=1)

class SummarizeResponse(BaseModel):
    summary: str

class SimilarityRequest(BaseModel):
    query: str = Field(..., min_length=1)
    texts: List[str] = Field(..., min_items=1)

class SimilarityResponse(BaseModel):
    closest_text: str
    score: float = Field(..., ge=0, le=1)

class HealthResponse(BaseModel):
    status: str
    uptime: float