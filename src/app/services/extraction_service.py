"""Extraction service for handling text extraction from PDF and text files.
"""

import PyPDF2

from typing import List, Tuple
from app.config import LINES_PER_PAGE

def extract_text_from_pdf(pdf_path: str) -> Tuple[str, int]:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Tuple of (extracted text as string, page count)
    """
    text = ""
    page_count = 0
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            page_count = len(pdf_reader.pages)
            
            for page_num in range(page_count):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text() or ""
                # Remove null characters that can cause issues
                page_text = page_text.replace('\u0000', '')
                text += page_text + "\n"
                
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
        
    return text, page_count


def extract_text_from_file(file_path: str) -> Tuple[str, int]:
    """
    Extract text content from various file types.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Tuple of (extracted text, estimated page count)
    """
    if file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    else:
        # Handle text files (txt, md, etc.)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                # Estimate page count based on line count
                page_count = max(1, len(content.splitlines()) // LINES_PER_PAGE)
                return content, page_count
        except Exception as e:
            print(f"Error reading text file {file_path}: {e}")
            return "", 1

