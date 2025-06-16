"""
Configuration settings for the document chunking module.

This module centralizes all configuration options for easier maintenance
and environment-specific customization.
"""

import os
from typing import List
from pathlib import Path
import re

# Environment settings
DEBUG_MODE = os.getenv('CHUNKING_DEBUG', 'TRUE').lower() == 'true'

# Directory settings

ROOT_DIR = os.getenv('CHUNKING_ROOT_DIR', 'kb_new')
UPLOAD_DIR = os.getenv('CHUNKING_UPLOAD_DIR', 'new_user_uploads')

# File processing settings
ALLOWED_FILETYPES = ['.md', '.docx', '.pdf', '.txt']
MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '50'))

# Chunking settings
MAX_CHUNK_TOKENS = int(os.getenv('MAX_CHUNK_TOKENS', '300')) 
MIN_CHUNK_TOKENS = int(os.getenv('MIN_CHUNK_TOKENS', '50')) 
OVERLAP_TOKENS = int(os.getenv('OVERLAP_TOKENS', '80'))        

# Text processing settings
REMOVE_ARTIFACTS = ['[image]', '[]', '[figure]', '[table]']
PRESERVE_FORMATTING = ['```', '`', '**', '*', '__', '_']

# Model settings
ENCODING_MODEL = os.getenv('ENCODING_MODEL', 'gpt-3.5-turbo')
TOKEN_ESTIMATION_RATIO = float(os.getenv('TOKEN_ESTIMATION_RATIO', '0.75'))

# Output settings
CHUNK_SEPARATOR = ' [SEP] '
DEFAULT_SECTION_NAME = 'Full Document'

# Compiled regex patterns for better performance
# Updated to detect both dash-based TOCs and dot-based TOCs (common in PDFs)
TOC_PATTERN = re.compile(r'(- .*\r?\n\r?\n[A-Z]|\.{3,}.*\d+\s*\n)')
# Pattern to detect dot-based table of contents entries
DOT_TOC_PATTERN = re.compile(r'^[^.\n]+\.{3,}.*\d+\s*$', re.MULTILINE)
# Pattern to detect the end of TOC and start of content
TOC_END_PATTERN = re.compile(r'\n\s*\n\s*([A-Z][a-z]+|\w+\s+[A-Z])')
LINE_ENDING_PATTERN = re.compile(r'\r\n|\r')
PARAGRAPH_BREAK_PATTERN = re.compile(r'\n{2,}')
WHITESPACE_PATTERN = re.compile(r'(?<!\n) +')
NEWLINE_REPLACE_PATTERN = re.compile(r'(?<!\n)\n(?!(\n|- ))')
BULLET_NUMBERED_PATTERN = re.compile(r'\n- |\n\d+\.')
SENTENCE_SPLIT_PATTERN = re.compile(r'(?<=[.!?])\s+')
LINES_PER_PAGE = 40  # Estimate for text files

# Validation settings
def validate_config():
    """Validate configuration settings."""
    if MAX_CHUNK_TOKENS <= MIN_CHUNK_TOKENS:
        raise ValueError("MAX_CHUNK_TOKENS must be greater than MIN_CHUNK_TOKENS")
    
    if OVERLAP_TOKENS >= MIN_CHUNK_TOKENS:
        raise ValueError("OVERLAP_TOKENS must be less than MIN_CHUNK_TOKENS")
    
    if not Path(ROOT_DIR).exists():
        print(f"Warning: ROOT_DIR '{ROOT_DIR}' does not exist")

if __name__ == "__main__":
    validate_config()
    print("Configuration validation passed!")
