from typing import List
from openai import AsyncOpenAI
from ..core.config import settings

# Configure OpenAI
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def generate_summary(text: str) -> str:
    response = await client.responses.create(
        model="gpt-4.1",
        instructions="Analyze the text, provide a title or identify the pragmatic, and summarize it. Return a max of 30 words",
        input=text
    )
    return response.output_text

async def find_most_similar(query: str, texts: List[str]) -> tuple[str, float]:
    query_embedding = await client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    query_vector = query_embedding.data[0].embedding

    texts_embeddings = await client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    
    max_similarity = -1
    closest_text = ""
    
    for idx, embedding in enumerate(texts_embeddings.data):
        similarity_score = cosine_similarity(query_vector, embedding.embedding)
        if similarity_score > max_similarity:
            max_similarity = similarity_score
            closest_text = texts[idx]

    return closest_text, max_similarity

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = sum(a * a for a in vec1) ** 0.5
    norm2 = sum(b * b for b in vec2) ** 0.5
    return dot_product / (norm1 * norm2)