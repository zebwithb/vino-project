"""
Vector Database Service Module

This module provides a service layer for managing ChromaDB vector database operations.
It handles document storage, retrieval, and semantic search capabilities for the application.

The service supports two operational modes:
1. Local persistent storage using ChromaDB's PersistentClient
2. Remote server connection using ChromaDB's HttpClient (for Docker deployments)

Main responsibilities:
- Initialize and manage ChromaDB collections for frameworks and user documents
- Store document chunks with embeddings using Google's Generative AI embedding function
- Perform semantic similarity searches across stored documents
- Automatically load framework documentation on startup
- Provide document management utilities (summaries, metadata handling)
"""
## TODO Error Handling: Consider more specific error handling for ChromaDB operations
import os
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from typing import List, Dict, Any, Optional

from app import config
from app.models import ProcessingResult
from app.services.document_service import load_docs_from_directory_to_list

class VectorDBService:
    """
    Vector Database Service for managing document embeddings and semantic search.
    
    This service provides a unified interface for storing and querying document chunks
    using ChromaDB as the vector database backend. It manages two separate collections:
    - Framework documents: Pre-loaded documentation and reference materials
    - User documents: User-uploaded files and custom content
    
    The service automatically handles:
    - ChromaDB client initialization (local or remote)
    - Google Generative AI embeddings for semantic search
    - Collection management and document persistence
    - Framework documentation auto-loading on startup
    
    Attributes:
        client: ChromaDB client instance (PersistentClient or HttpClient)
        google_ef: Google Generative AI embedding function
        frameworks_collection: ChromaDB collection for framework documents
        user_documents_collection: ChromaDB collection for user documents
    """
    
    def __init__(self):
        """
        Initialize the VectorDBService with ChromaDB client and collections.
        
        Sets up the ChromaDB client based on configuration (local vs server mode),
        initializes Google embedding function, creates or connects to collections,
        and automatically loads framework documents if the collection is empty.
        """
        # Initialize ChromaDB client based on configuration
        if config.USE_CHROMA_SERVER:
            print(f"Connecting to ChromaDB server at {config.CHROMA_SERVER_URL}")
            self.client = chromadb.HttpClient(
                host=config.CHROMA_SERVER_HOST,
                port=config.CHROMA_SERVER_PORT
            )        
        else:
            print(f"Using local ChromaDB persistent client at {config.CHROMA_DB_PATH}")
            self.client = chromadb.PersistentClient(path=config.CHROMA_DB_PATH)
        
        # Initialize Google Generative AI embedding function for semantic search
        self.google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
            api_key=config.GOOGLE_API_KEY.get_secret_value()
        )
        
        # Create or connect to collections
        self.frameworks_collection = self._get_or_create_collection(config.FRAMEWORKS_COLLECTION_NAME)
        self.user_documents_collection = self._get_or_create_collection(config.USER_DOCUMENTS_COLLECTION_NAME)
        
        # Auto-load framework documents on startup
        self._initialize_framework_docs()

    def _get_or_create_collection(self, name: str):
        """
        Get an existing collection or create a new one with the specified name.
        
        Args:
            name (str): Name of the collection to get or create
            
        Returns:
            chromadb.Collection: The ChromaDB collection instance
            
        Raises:
            Exception: If collection creation/retrieval fails
        """
        try:
            return self.client.get_or_create_collection(
                name=name,
                embedding_function=self.google_ef  # type: ignore
            )
        except Exception as e:
            print(f"Error getting or creating collection {name}: {e}")
            raise

    def _initialize_framework_docs(self):
        """
        Initialize framework documents collection by loading from the configured directory.
        
        This method checks if the frameworks collection is empty and automatically
        loads documents from the DOCUMENTS_DIR if available. This ensures that
        framework documentation is always available for semantic search.
        
        The method handles:
        - Empty collection detection
        - Directory validation
        - Bulk document loading
        - Error handling and user feedback
        """
        if self.frameworks_collection.count() == 0:
            print(f"Frameworks collection '{config.FRAMEWORKS_COLLECTION_NAME}' is empty. Loading documents from {config.DOCUMENTS_DIR}...")
            if not os.path.exists(config.DOCUMENTS_DIR) or not os.listdir(config.DOCUMENTS_DIR):
                print(f"Warning: Framework documents directory '{config.DOCUMENTS_DIR}' is empty or does not exist. No framework documents will be loaded.")
                return

            processing_result = load_docs_from_directory_to_list(config.DOCUMENTS_DIR)
            if processing_result.documents_processed_texts:
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
        """
        Add processed documents to the specified collection.
        
        Takes a ProcessingResult containing document chunks, metadata, and IDs,
        and stores them in the appropriate ChromaDB collection with embeddings.
        
        Args:
            collection_name (str): Name of the target collection 
                                 (frameworks or user_documents)
            processing_result (ProcessingResult): Processed document data containing
                                                text chunks, metadata, and IDs
                                                
        Returns:
            bool: True if documents were successfully added, False otherwise
            
        Note:
            - Metadata values are converted to strings for ChromaDB compatibility
            - Handles duplicate ID errors gracefully
            - Provides detailed error logging
        """
        collection = self.frameworks_collection if collection_name == config.FRAMEWORKS_COLLECTION_NAME else self.user_documents_collection
        if not processing_result.documents_processed_texts:
            print(f"No documents to add to {collection_name}.")
            return False
        try:
            collection.add(
                documents=processing_result.documents_processed_texts,
                metadatas=[{k: str(v) for k, v in metadata.items()} for metadata in processing_result.metadatas_for_db],
                ids=processing_result.ids_for_db
            )
            return True
        except Exception as e:
            print(f"Error adding documents to collection {collection_name}: {e}")
            # Consider more specific error handling, e.g., for duplicate IDs
            if "ID already exists" in str(e):
                print("Some documents might already exist in the collection.")
            return False

    def query_collection(self, collection_name: str, query_texts: List[str], n_results: int = 3) -> Dict[str, Optional[List[Any]]]:
        """
        Perform semantic search on the specified collection.
        
        Uses the Google Generative AI embedding function to find semantically
        similar documents to the provided query texts. Returns the most similar
        document chunks along with their metadata and similarity scores.
        
        Args:
            collection_name (str): Name of the collection to search 
                                 (frameworks or user_documents)
            query_texts (List[str]): List of query strings to search for
            n_results (int, optional): Maximum number of results per query. 
                                     Defaults to 3.
                                     
        Returns:
            Dict[str, Optional[List[Any]]]: Dictionary containing:
                - ids: List of document chunk IDs
                - documents: List of document text chunks
                - metadatas: List of document metadata
                - distances: List of similarity distances (lower = more similar)
                
        Note:
            - Returns None values for each field if query fails
            - Distances represent semantic similarity (lower values = more similar)
            - Results are automatically ranked by similarity
        """
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
        """
        Get a summary of user-uploaded documents and their chunk counts.
        
        Retrieves metadata from all documents in the user documents collection
        and provides a summary showing each filename and how many chunks it
        was split into during processing.
        
        Returns:
            List[Dict[str, Any]]: List of dictionaries containing:
                - filename: Original filename of the uploaded document
                - chunks_in_db: Number of chunks stored for this document
                
        Note:
            - This operation can be memory intensive for very large collections
            - Consider implementing pagination for large document sets
            - Returns empty list if retrieval fails
            
        Example:
            [
                {"filename": "document1.pdf", "chunks_in_db": 15},
                {"filename": "document2.txt", "chunks_in_db": 8}
            ]
        """
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

# Instantiate the service so it can be imported and used throughout the application
# This creates a singleton instance that maintains the ChromaDB connection
vector_db_service = VectorDBService()