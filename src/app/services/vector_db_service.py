import os
from dotenv import load_dotenv

import chromadb
import chromadb.utils.embedding_functions as embedding_functions

from config import CHROMA_DB_PATH, NEW_DOCUMENTS_DIR
from app.services.ingestion_service import load_documents_from_directory

load_dotenv()


def initialize_vector_db():
    """
    Initialize ChromaDB and load documents if needed.
    
    Returns:
        tuple: (frameworks_collection, user_documents_collection)
    """
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=api_key)
    
    try:
        # Create or get the frameworks collection
        collection_fw = client.get_or_create_collection(
            name="frameworks", 
            embedding_function=google_ef
        )
        
        # Create or get the user documents collection
        collection_user = client.get_or_create_collection(
            name="user_documents",
            embedding_function=google_ef
        )

        # Process documents only if needed
        if collection_fw.count() == 0:
            print("Frameworks collection is empty. Loading documents...")
            documents, metadatas, ids, message = load_documents_from_directory(NEW_DOCUMENTS_DIR)
            
            for metadata in metadatas:
                if metadata and 'keywords' in metadata and isinstance(metadata['keywords'], list):
                    metadata['keywords'] = ', '.join(metadata['keywords'])
            
            # Add documents to collection if any were loaded
            if documents:
                for doc, metadata, doc_id in zip(documents, metadatas, ids):
                    if metadata.get('source') == 'user_upload':
                        collection_user.add(documents=[doc], metadatas=[metadata], ids=[doc_id])
                    else:
                        collection_fw.add(documents=[doc], metadatas=[metadata], ids=[doc_id])
                
                print(f"Added {len(documents)} document chunks to the frameworks collection.")
            else:
                print("No documents were loaded. Please check the directory path.")
        else:
            print(f"Using existing frameworks collection with {collection_fw.count()} document chunks.")
        
        print(f"User documents collection has {collection_user.count()} document chunks.")
        return collection_fw, collection_user

    except Exception as e:
        print(f"Error initializing ChromaDB collection: {e}")
        raise

def list_documents_in_collection(collection_name=None):
    """
    List all documents in a specific collection or in all collections.
    
    Args:
        collection_name (str, optional): The name of the collection to query. 
                                         If None, lists documents from all collections.
    
    Returns:
        dict: Information about the queried collection(s)
    """
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    
    if collection_name:
        collections = [client.get_collection(name=collection_name)]
    else:
        collections = [
            client.get_collection(name="frameworks"),
            client.get_collection(name="user_documents")
        ]
    
    results = {}
    
    for collection in collections:
        # Get all documents from the collection
        documents = collection.get()
        
        # Format the results
        collection_data = {
            "count": collection.count(),
            "documents": []
        }
        
        # Add document details
        for i in range(len(documents["ids"])):
            metadata = documents["metadatas"][i] if documents["metadatas"] else None
            
            # Display all metadata fields as they exist in the database
            if metadata:
                print(f"\n--- Document {i+1} ---")
                print(f"ID: {documents['ids'][i]}")
                
                # Document-level metadata
                print(f"Doc ID: {metadata.get('doc_id')}")
                print(f"Chunk Number: {metadata.get('chunk_number')}")
                print(f"Chunk Length: {metadata.get('chunk_length')}")
                print(f"Section: {metadata.get('section')}")
                
                # File-level metadata
                print(f"Source: {metadata.get('source')}")
                print(f"Filename: {metadata.get('filename')}")
                print(f"File Size: {metadata.get('file_size')} bytes")
                print(f"File Type: {metadata.get('file_type')}")
                print(f"Page Count: {metadata.get('page_count')}")
                print(f"Word Count: {metadata.get('word_count')}")
                print(f"Character Count: {metadata.get('char_count')}")
                print(f"Keywords: {metadata.get('keywords')}")
                print(f"Abstract: {metadata.get('abstract', '')[:100]}...")
            else:
                print(f"\n--- Document {i+1} ---")
                print(f"ID: {documents['ids'][i]}")
                print("No metadata available")
            
            doc_info = {
                "id": documents["ids"][i],
                "metadata": metadata,
                "text_preview": documents["documents"][i][:100] + "..." if documents["documents"][i] else None
            }
            collection_data["documents"].append(doc_info)
            
            # Show text preview
            print(f"Text Preview: {documents['documents'][i][:150]}...")
            print("-" * 50)
        
        results[collection.name] = collection_data
        print(f"\nCollection '{collection.name}' has {collection.count()} documents total.\n")
        
    return results


# Get API key from environment
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set the GOOGLE_API_KEY environment variable.")

def delete_all_documents(collection_name=None):
    """
    Delete all documents from a specific collection or from all collections.
    
    Args:
        collection_name (str, optional): The name of the collection to clear.
                                         If None, clears all collections.
    
    Returns:
        dict: Information about the deletion operation
    """
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    
    if collection_name:
        collections = [client.get_collection(name=collection_name)]
    else:
        collections = [
            client.get_collection(name="frameworks"),
            client.get_collection(name="user_documents")
        ]
    
    results = {}
    
    for collection in collections:
        # Get all document IDs
        documents = collection.get()
        doc_ids = documents["ids"]
        
        # Delete all documents
        if doc_ids:
            collection.delete(ids=doc_ids)
            results[collection.name] = {
                "deleted_count": len(doc_ids),
                "status": "success"
            }
            print(f"Deleted {len(doc_ids)} documents from collection '{collection.name}'.")
        else:
            results[collection.name] = {
                "deleted_count": 0,
                "status": "no documents found"
            }
            print(f"No documents to delete in collection '{collection.name}'.")
    
    return results

# delete_all_documents("frameworks")
# delete_all_documents("user_documents")
# initialize_vector_db()
# list_documents_in_collection("user_documents")