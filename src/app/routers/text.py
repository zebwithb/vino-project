from fastapi import APIRouter, HTTPException
from ..schemas.text import (
    SummarizeRequest, 
    SummarizeResponse, 
    SimilarityRequest, 
    SimilarityResponse
)
from ..services.text_analysis import generate_summary, find_most_similar

router = APIRouter(prefix="/v1", tags=["text"])

@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(request: SummarizeRequest):
    try:
        summary = await generate_summary(request.text)
        return SummarizeResponse(summary=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/similarity", response_model=SimilarityResponse)
async def similarity(request: SimilarityRequest):
    try:
        closest_text, score = await find_most_similar(request.query, request.texts)
        return SimilarityResponse(
            closest_text=closest_text,
            score=score
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))