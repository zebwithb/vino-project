"""Service for extracting and generating metadata from documents.
"""


import os
import re

from collections import Counter
from typing import List, Tuple
from app.schemas.models import FileMetadata, FileType

from app.config import DEFAULT_MAX_KEYWORDS, DEFAULT_ABSTRACT_LENGTH, STOPWORDS



def char_word_count(text: str) -> Tuple[int, int]:
    """
    Count the number of characters and words in a string.
    
    Args:
        text: The input string
        
    Returns:
        Tuple of (character count, word count)
    """
    char_count = len(text)
    word_count = len(text.split()) if text.strip() else 0
    return char_count, word_count


def extract_keywords(text: str, max_keywords: int = DEFAULT_MAX_KEYWORDS) -> List[str]:
    """
    Extract keywords from text using simple frequency analysis.
    
    Args:
        text: Document content
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List of top keywords
    """
    # Convert to lowercase and extract words (3+ characters)
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Filter out stopwords
    filtered_words = [word for word in words if word not in STOPWORDS]
    
    # Count word frequencies and get most common
    word_counts = Counter(filtered_words)
    return [word for word, _ in word_counts.most_common(max_keywords)]


def generate_abstract(text: str, max_length: int = DEFAULT_ABSTRACT_LENGTH) -> str:
    """
    Generate a simple abstract by taking the first part of the document.
    
    Args:
        text: Document content
        max_length: Maximum length of abstract
        
    Returns:
        Document abstract
    """
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Take the first part of the document
    abstract = text[:max_length]
    
    # Try to end at a sentence boundary for better readability
    if len(text) > max_length:
        last_period = abstract.rfind('.')
        if last_period > max_length // 2:  # Only trim if we have enough text
            abstract = abstract[:last_period + 1]
    
    return abstract


def create_file_metadata(file_path: str, content: str, page_count: int, 
                        source: str = "system_upload") -> FileMetadata:
    """
    Create file-level metadata for a document.
    
    Args:
        file_path: Path to the source document
        content: Document content
        page_count: Number of pages in the document
        source: Source identifier for the document
        
    Returns:
        FileMetadata object containing document statistics and metadata
    """
    file_name = os.path.basename(file_path)
    char_count, word_count = char_word_count(content)
    file_size = os.path.getsize(file_path)
    keywords = extract_keywords(content)
    abstract = generate_abstract(content)
    file_extension = os.path.splitext(file_path)[1].lstrip('.').lower()
    
    return FileMetadata(
        source=source,
        filename=file_name,
        file_size=file_size,
        file_type=file_extension,
        page_count=page_count,
        file_word_count=word_count,
        file_char_count=char_count,
        keywords=keywords,
        abstract=abstract
    )

