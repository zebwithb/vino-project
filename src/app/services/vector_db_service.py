import os
from typing import List, Dict, Any, Optional, Tuple

import chromadb
import chromadb.utils.embedding_functions as embedding_functions

from app.core.config import settings
from app.schemas.models import ProcessingResult


class VectorDBService:
    """Service for managing ChromaDB vector database operations."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize ChromaDB client and setup."""
        self.db_path = db_path or settings.CHROMA_DB_PATH
        self.client = None
        self.google_ef = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the ChromaDB client and embedding function."""
        try:
            # Ensure the database directory exists
            os.makedirs(self.db_path, exist_ok=True)
            
            # Initialize ChromaDB client with persistent storage
            self.client = chromadb.PersistentClient(path=self.db_path)
            
            # Initialize Google embedding function
            self.google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
                api_key=settings.GOOGLE_API_KEY.get_secret_value()
            )
            
            print(f"ChromaDB client initialized at: {self.db_path}")
        except Exception as e:
            print(f"Error initializing ChromaDB client: {e}")
            raise
    
    def get_or_create_collection(self, collection_name: str):
        """Get existing collection or create new one with Google embedding function."""
        try:
            return self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.google_ef
            )
        except Exception as e:
            print(f"Error getting/creating collection {collection_name}: {e}")
            raise
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> bool:
        """Add documents to a ChromaDB collection."""
        try:
            collection = self.get_or_create_collection(collection_name)
            
            # Process metadatas to handle keywords list
            processed_metadatas = []
            for metadata in metadatas:
                processed_metadata = metadata.copy()
                if 'keywords' in processed_metadata and isinstance(processed_metadata['keywords'], list):
                    processed_metadata['keywords'] = ', '.join(processed_metadata['keywords'])
                processed_metadatas.append(processed_metadata)
            
            collection.add(
                documents=documents,
                metadatas=processed_metadatas,
                ids=ids
            )
            
            print(f"Successfully added {len(documents)} documents to collection '{collection_name}'")
            return True
            
        except Exception as e:
            print(f"Error adding documents to collection {collection_name}: {e}")
            return False
    
    def add_processing_result(
        self,
        collection_name: str,
        processing_result: ProcessingResult
    ) -> bool:
        """Add a ProcessingResult to ChromaDB collection."""
        try:
            # Convert ProcessingResult to the format ChromaDB expects
            documents = processing_result.chunk_all_texts
            ids = processing_result.chunk_ids
            
            # Convert Pydantic models to dictionaries for ChromaDB
            metadatas = []
            for doc_meta, file_meta in zip(processing_result.doc_metadatas, processing_result.file_metadatas):
                combined_metadata = {
                    **doc_meta.model_dump(),
                    **file_meta.model_dump()
                }
                metadatas.append(combined_metadata)
            
            return self.add_documents(
                collection_name=collection_name,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
        except Exception as e:
            print(f"Error adding ProcessingResult to collection {collection_name}: {e}")
            return False
    
    def query_collection(
        self,
        collection_name: str,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query documents from a ChromaDB collection."""
        try:
            collection = self.get_or_create_collection(collection_name)
            
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where
            )
            
            return results
            
        except Exception as e:
            print(f"Error querying collection {collection_name}: {e}")
            return {}
    
    def list_collections(self) -> List[str]:
        """List all available collections."""
        try:
            collections = self.client.list_collections()
            return [collection.name for collection in collections]
        except Exception as e:
            print(f"Error listing collections: {e}")
            return []
    
    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection."""
        try:
            self.client.delete_collection(name=collection_name)
            print(f"Successfully deleted collection '{collection_name}'")
            return True
        except Exception as e:
            print(f"Error deleting collection {collection_name}: {e}")
            return False
    
    def get_collection_count(self, collection_name: str) -> int:
        """Get the number of documents in a collection."""
        try:
            collection = self.get_or_create_collection(collection_name)
            return collection.count()
        except Exception as e:
            print(f"Error getting count for collection {collection_name}: {e}")
            return 0
    
    def get_collection_documents(self, collection_name: str) -> Dict[str, Any]:
        """Get all documents from a collection."""
        try:
            collection = self.get_or_create_collection(collection_name)
            return collection.get()
        except Exception as e:
            print(f"Error getting documents from collection {collection_name}: {e}")
            return {}
    
    def delete_all_documents(self, collection_name: str) -> Dict[str, Any]:
        """Delete all documents from a specific collection."""
        try:
            collection = self.get_or_create_collection(collection_name)
            
            # Get all document IDs
            documents = collection.get()
            doc_ids = documents["ids"]
            
            # Delete all documents
            if doc_ids:
                collection.delete(ids=doc_ids)
                result = {
                    "deleted_count": len(doc_ids),
                    "status": "success"
                }
                print(f"Deleted {len(doc_ids)} documents from collection '{collection_name}'.")
            else:
                result = {
                    "deleted_count": 0,
                    "status": "no documents found"
                }
                print(f"No documents to delete in collection '{collection_name}'.")
            
            return result
              except Exception as e:
            print(f"Error deleting documents from collection {collection_name}: {e}")
            return {"deleted_count": 0, "status": "error", "error": str(e)}