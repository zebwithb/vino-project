import sys
import re 
from typing import List, Union 
from openai import AsyncOpenAI
from loguru import logger
from langchain.text_splitter import RecursiveCharacterTextSplitter 
from ..core.config import settings

logger.remove()
logger.add(sys.stdout, serialize=True, enqueue=True)

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

def split_text_recursively(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
    separators: List[str] = None
) -> List[str]:
    """
    Splits text recursively using LangChain's RecursiveCharacterTextSplitter.

    Args:
        text: The text to split.
        chunk_size: The target size for each chunk (in characters).
        chunk_overlap: The number of characters to overlap between chunks.
        separators: Optional list of separators to use. Defaults to ["\n\n", "\n", " ", ""].

    Returns:
        A list of text chunks.
    """
    if separators is None:
        separators = ["\n\n", "\n", " ", ""]

    logger.info(f"Splitting text recursively. Chunk size: {chunk_size}, Overlap: {chunk_overlap}")

    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
            separators=separators,
        )
        chunks = text_splitter.split_text(text)
        logger.info(f"Text split into {len(chunks)} chunks.")
        return chunks
    except Exception as e:
        logger.exception("Error during recursive text splitting.")
        # Depending on requirements, you might return [] or re-raise
        return []

async def get_embeddings(texts: Union[str, List[str]], model: str = "text-embedding-3-small") -> Union[List[float], List[List[float]]]:
    """
    Generates embeddings for a single text or a list of texts.

    Args:
        texts: A single string or a list of strings to embed.
                 If providing chunks, pass the list of chunk strings.
        model: The embedding model to use.

    Returns:
        A single embedding vector if input is a string, or a list of embedding vectors if input is a list of strings.

    Raises:
        Exception: If the OpenAI API call fails.
    """
    try:
        is_single_text = isinstance(texts, str)
        input_data = [texts] if is_single_text else texts

        if not input_data:  # Handle empty list input
            logger.warning("get_embeddings called with empty list.")
            return []

        logger.info(f"Requesting embeddings for {len(input_data)} text(s) using model {model}.")
        response = await client.embeddings.create(
            model=model,
            input=input_data
        )

        embeddings = [data.embedding for data in response.data]
        logger.info(f"Successfully retrieved {len(embeddings)} embedding(s).")

        return embeddings[0] if is_single_text else embeddings
    except Exception as e:
        logger.exception(f"Error getting embeddings with model {model}.")
        raise  # Re-raise the exception to be handled upstream

async def generate_summary(text: str, max_words: int = 30) -> str:
    try:
        # --- Preprocessing ---
        # Normalize whitespace: replace multiple spaces/newlines/tabs with a single space
        processed_text = re.sub(r'\s+', ' ', text).strip()
        # Optional: Add more cleaning steps here if needed
        # ---------------------

        logger.info("Generating summary for text.", original_length=len(text), processed_length=len(processed_text))
        if not processed_text:
             logger.warning("Input text became empty after processing.")
             return "" 

        response = await client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": f"Summarize the following text in approximately {max_words} words. Identify the main topic or provide a concise title as part of the summary."},
                {"role": "user", "content": processed_text} # Use processed text
            ],
            max_tokens=max_words + 20,
            temperature=0.5,
        )
        summary = response.choices[0].message.content.strip()
        logger.info("Summary generated successfully.", summary_length=len(summary))
        return summary
    except Exception as e:
        logger.exception("Error during summarization.")
        raise

async def find_most_similar(query: str, texts: List[str]) -> tuple[str, float]:
    try:
        logger.info("Finding most similar text.", query=query, num_texts=len(texts))

        if not texts:
            logger.warning("find_most_similar called with empty texts list.")
            return "", 0.0
        
        query_vector = await get_embeddings(query)
        texts_vectors = await get_embeddings(texts)

        if not texts_vectors:  # Check if embedding failed for texts
            logger.error("Failed to get embeddings for the provided texts.")
            return "", 0.0  # Or raise an error

        max_similarity = -1.0
        closest_text = ""
        closest_text_index = -1

        for idx, text_vector in enumerate(texts_vectors):
            similarity_score = cosine_similarity(query_vector, text_vector)
            if similarity_score > max_similarity:
                max_similarity = similarity_score
                closest_text_index = idx

        if closest_text_index != -1:
            closest_text = texts[closest_text_index]
        elif texts:  # Fallback if no similarity > -1 found but texts exist
            closest_text = texts[0]
            logger.warning("Could not determine closest text based on similarity > -1, defaulting to first text.")
        else:
            # This case should ideally not be reached due to the initial check
            logger.error("No texts available to determine the closest one.")
            return "", 0.0

        logger.info("Similarity calculation successful.", closest_text=closest_text, score=max_similarity)
        return closest_text, max_similarity
    except Exception as e:
        logger.exception("Error during similarity calculation.")
        raise

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    norm1 = sum(a * a for a in vec1) ** 0.5
    norm2 = sum(b * b for b in vec2) ** 0.5
    if norm1 == 0 or norm2 == 0:
        logger.warning("Attempted cosine similarity with zero vector.")
        return 0.0
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    similarity = dot_product / (norm1 * norm2)
    # Clamp value due to potential floating point inaccuracies
    return max(-1.0, min(1.0, similarity))