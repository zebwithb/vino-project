import os
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from typing import List, Dict, Any, Optional

from app import config
from app.models import ProcessingResult
from app.services.document_service import load_docs_from_directory_to_list

class VectorDBService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=config.CHROMA_DB_PATH)
        self.google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=config.GOOGLE_API_KEY)
        
        self.frameworks_collection = self._get_or_create_collection(config.FRAMEWORKS_COLLECTION_NAME)
        self.user_documents_collection = self._get_or_create_collection(config.USER_DOCUMENTS_COLLECTION_NAME)
        
        self._initialize_framework_docs()

    def _get_or_create_collection(self, name: str):
        try:
            return self.client.get_or_create_collection(
                name=name,
                embedding_function=self.google_ef
            )
        except Exception as e:
            print(f"Error getting or creating collection {name}: {e}")
            raise

    def _initialize_framework_docs(self):
        if self.frameworks_collection.count() == 0:
            print(f"Frameworks collection '{config.FRAMEWORKS_COLLECTION_NAME}' is empty. Loading documents from {config.DOCUMENTS_DIR}...")
            if not os.path.exists(config.DOCUMENTS_DIR) or not os.listdir(config.DOCUMENTS_DIR):
                print(f"Warning: Framework documents directory '{config.DOCUMENTS_DIR}' is empty or does not exist. No framework documents will be loaded.")
                return

            processing_result = load_docs_from_directory_to_list(config.DOCUMENTS_DIR)
            if processing_result.documents:
                self.add_documents(
                    collection_name=config.FRAMEWORKS_COLLECTION_NAME,
                    processing_result=processing_result
                )
                print(f"Added {processing_result.chunk_count} document chunks to the frameworks collection.")
            else:
                print("No framework documents were loaded. Please check the directory path and file contents.")
        else:
            print(f"Using existing frameworks collection with {self.frameworks_collection.count()} document chunks.")
        print(f"User documents collection has {self.user_documents_collection.count()} document chunks.")


    def add_documents(self, collection_name: str, processing_result: ProcessingResult) -> bool:
        collection = self.frameworks_collection if collection_name == config.FRAMEWORKS_COLLECTION_NAME else self.user_documents_collection
        if not processing_result.documents:
            print(f"No documents to add to {collection_name}.")
            return False
        try:
            collection.add(
                documents=processing_result.documents,
                metadatas=[{k: str(v) for k, v in metadata.items()} for metadata in processing_result.metadatas],
                ids=processing_result.ids
            )
            return True
        except Exception as e:
            print(f"Error adding documents to collection {collection_name}: {e}")
            # Consider more specific error handling, e.g., for duplicate IDs
            if "ID already exists" in str(e):
                print("Some documents might already exist in the collection.")
            return False

    def query_collection(self, collection_name: str, query_texts: List[str], n_results: int = 3) -> Dict[str, Optional[List[Any]]]:
        collection = self.frameworks_collection if collection_name == config.FRAMEWORKS_COLLECTION_NAME else self.user_documents_collection
        try:
            query_result = collection.query(query_texts=query_texts, n_results=n_results)
            return {
                "ids": query_result["ids"] if "ids" in query_result else None,
                "documents": query_result["documents"] if "documents" in query_result else None,
                "metadatas": query_result["metadatas"] if "metadatas" in query_result else None,
                "distances": query_result["distances"] if "distances" in query_result else None
            }
        except Exception as e:
            print(f"Error querying collection {collection_name}: {e}")
            return {"ids": None, "documents": None, "metadatas": None, "distances": None} # Ensure consistent error return

    def get_user_document_summary(self) -> List[Dict[str, Any]]:
        """Gets a summary of filenames and chunk counts for user documents."""
        user_doc_summary = []
        try:
            # Fetch all metadatas. This can be memory intensive for very large collections.
            # Consider alternative strategies if performance becomes an issue.
            all_docs = self.user_documents_collection.get(include=["metadatas"])
            
            if all_docs and all_docs["metadatas"]:
                file_chunk_counts: Dict[str, int] = {}
                for metadata in all_docs["metadatas"]:
                    if metadata and "filename" in metadata:
                        filename = metadata["filename"]
                        file_chunk_counts[str(filename)] = file_chunk_counts.get(str(filename), 0) + 1
                
                for filename, count in file_chunk_counts.items():
                    user_doc_summary.append({"filename": filename, "chunks_in_db": count})
            return user_doc_summary
        except Exception as e:
            print(f"Error retrieving user document summary: {str(e)}")
            return []

# Instantiate the service so it can be imported
vector_db_service = VectorDBService()