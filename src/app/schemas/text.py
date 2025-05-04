
from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=1, example="This is a long article about AI and its impact on society.")

    class Config:
        schema_extra = {
            "example": {
                "text": "This is a long article about AI and its impact on society."
            }
        }

class SummarizeResponse(BaseModel):
    summary: str

    class Config:
        schema_extra = {
            "example": {
                "summary": "AI is transforming society in many ways."
            }
        }

class SimilarityRequest(BaseModel):
    query: str = Field(..., min_length=1, example="What is artificial intelligence?")
    texts: list[str] = Field(..., min_items=1, example=[
        "Artificial intelligence is the simulation of human intelligence in machines.",
        "Machine learning is a subset of AI.",
        "Deep learning is a technique for implementing machine learning."
    ])

    class Config:
        schema_extra = {
            "example": {
                "query": "What is artificial intelligence?",
                "texts": [
                    "Artificial intelligence is the simulation of human intelligence in machines.",
                    "Machine learning is a subset of AI.",
                    "Deep learning is a technique for implementing machine learning."
                ]
            }
        }

class SimilarityResponse(BaseModel):
    closest_text: str
    score: float = Field(..., ge=0, le=1)

    class Config:
        schema_extra = {
            "example": {
                "closest_text": "Artificial intelligence is the simulation of human intelligence in machines.",
                "score": 0.97
            }
        }

class HealthResponse(BaseModel):
    status: str
    uptime: float

    class Config:
        schema_extra = {
            "example": {
                "status": "ok",
                "uptime": 123.45
            }
        }