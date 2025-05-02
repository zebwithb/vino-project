import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import openai
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

app = FastAPI()
start_time = time.time()

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

@app.post("/v1/summarize", response_model=SummarizeResponse)
async def summarize(request: SummarizeRequest):
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize the following text in approximately 30 words:"},
                {"role": "user", "content": request.text}
            ]
        )
        return SummarizeResponse(summary=response.choices[0].message.content.strip())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/similarity", response_model=SimilarityResponse)
async def similarity(request: SimilarityRequest):
    try:
        # Get embedding for query
        query_embedding = await openai.Embedding.acreate(
            model="text-embedding-ada-002",
            input=request.query
        )
        query_vector = query_embedding.data[0].embedding

        # Get embeddings for all texts
        texts_embeddings = await openai.Embedding.acreate(
            model="text-embedding-ada-002",
            input=request.texts
        )
        
        # Calculate cosine similarity and find the most similar text
        max_similarity = -1
        closest_text = ""
        
        for idx, embedding in enumerate(texts_embeddings.data):
            similarity_score = cosine_similarity(query_vector, embedding.embedding)
            if similarity_score > max_similarity:
                max_similarity = similarity_score
                closest_text = request.texts[idx]

        return SimilarityResponse(
            closest_text=closest_text,
            score=max_similarity
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        uptime=time.time() - start_time
    )

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = sum(a * a for a in vec1) ** 0.5
    norm2 = sum(b * b for b in vec2) ** 0.5
    return dot_product / (norm1 * norm2)