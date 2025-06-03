import os
import glob
import PyPDF2
from typing import Tuple, Optional, List

from app import config
from app.models import ProcessingResult, DocumentMetadata

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
    return text

def process_document_content(
    file_path: str,
    content: str,
    chunk_size: int = config.CHUNK_SIZE,
    chunk_overlap: int = config.CHUNK_OVERLAP
) -> ProcessingResult:
    result = ProcessingResult()
    file_name = os.path.basename(file_path)
    doc_id_base = os.path.splitext(file_name)[0].replace(" ", "_")

    if not content.strip():
        print(f"Warning: No content extracted from {file_name}")
        return result

    start_index = 0
    chunk_number = 1
    while start_index < len(content):
        end_index = min(start_index + chunk_size, len(content))
        chunk_text = content[start_index:end_index]

        metadata = DocumentMetadata(
            source=file_path,
            filename=file_name,
            chunk=chunk_number
        ).model_dump()

        result.documents.append(chunk_text)
        result.metadatas.append(metadata)
        result.ids.append(f"{doc_id_base}_chunk_{chunk_number}")

        start_index += chunk_size - chunk_overlap
        if start_index >= end_index and end_index < len(content): # Ensure progress if overlap is large
             start_index = end_index
        chunk_number += 1
    
    result.chunk_count = chunk_number - 1
    return result

def load_docs_from_directory_to_list(directory_path: str) -> ProcessingResult:
    aggregated_result = ProcessingResult()
    
    txt_files = glob.glob(os.path.join(directory_path, "*.txt"))
    pdf_files = glob.glob(os.path.join(directory_path, "*.pdf"))
    file_paths = txt_files + pdf_files

    for file_path in file_paths:
        try:
            content = ""
            if file_path.lower().endswith('.pdf'):
                content = extract_text_from_pdf(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

            if content.strip():
                result = process_document_content(file_path, content)
                aggregated_result.documents.extend(result.documents)
                aggregated_result.metadatas.extend(result.metadatas)
                aggregated_result.ids.extend(result.ids)
                aggregated_result.chunk_count += result.chunk_count
                print(f"Loaded {result.chunk_count} chunks from document: {os.path.basename(file_path)}")
            else:
                print(f"No content extracted from {os.path.basename(file_path)}")


        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            
    return aggregated_result

def load_single_document(file_path: str) -> Tuple[Optional[ProcessingResult], str]:
    try:
        content = ""
        if file_path.lower().endswith('.pdf'):
            content = extract_text_from_pdf(file_path)
        elif file_path.lower().endswith(('.txt', '.md', '.py', '.js', '.html', '.css', '.json')): # Add more if needed
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        else:
            return None, f"Unsupported file type: {os.path.basename(file_path)}. Supported types are PDF and common text files."

        if not content.strip():
            return None, f"No content extracted from {os.path.basename(file_path)}"

        result = process_document_content(file_path, content)
        return result, f"Successfully processed {os.path.basename(file_path)} into {result.chunk_count} chunks"
    
    except Exception as e:
        return None, f"Error loading {file_path}: {str(e)}"

def store_uploaded_file(file_bytes: bytes, filename: str) -> Tuple[Optional[str], str]:
    """Stores uploaded file bytes to the user_uploads directory."""
    os.makedirs(config.USER_UPLOADS_DIR, exist_ok=True)
    destination_path = os.path.join(config.USER_UPLOADS_DIR, filename)
    try:
        with open(destination_path, 'wb') as f:
            f.write(file_bytes)
        return destination_path, f"File '{filename}' uploaded successfully."
    except Exception as e:
        return None, f"Error saving uploaded file '{filename}': {str(e)}"

def list_uploaded_files_in_dir() -> List[str]:
    if not os.path.exists(config.USER_UPLOADS_DIR):
        return []
    return [f for f in os.listdir(config.USER_UPLOADS_DIR) if os.path.isfile(os.path.join(config.USER_UPLOADS_DIR, f))]
