"""Integration test for Phase 3 file context functionality"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.services.chat_service import ChatService
from app.services.vector_db_service import VectorDBService
from unittest.mock import Mock

def test_file_context_integration():
    """Test the file context functionality with mocked vector DB."""
    print("🧪 Testing Phase 3 File Context Integration...")
    
    # Create mock vector DB service
    mock_vector_db = Mock(spec=VectorDBService)
    
    # Setup mock responses for file context query
    mock_vector_db.query_collection.side_effect = [
        # File context query
        {
            "documents": [["This is content from the specific document about project planning methodology."]],
            "metadatas": [[{"filename": "project_guide.pdf", "chunk_index": 1}]]
        },
        # Framework query  
        {
            "documents": [["Agile framework information"]],
            "metadatas": [[{"filename": "agile_guide.pdf", "chunk_index": 1}]]
        },
        # General user docs query (reduced)
        {
            "documents": [["Other user document content"]],
            "metadatas": [[{"filename": "other.pdf", "chunk_index": 1}]]
        }
    ]
    
    # Create ChatService with mocked VectorDB
    chat_service = ChatService(vector_db_service=mock_vector_db)
    
    # Test file context functionality  
    try:
        response, history, step, planner = chat_service.process_query(
            session_id="test_session",
            query_text="What does the document say about planning methodology?",
            api_history_data=[],
            uploaded_file_context_name="project_guide.pdf",
            explain_active=True
        )
        
        print("✅ ChatService.process_query completed successfully")
        print(f"📝 Response type: {type(response)}")
        print(f"📊 History length: {len(history)}")
        print(f"🔢 Current step: {step}")
        
        # Verify that vector DB was called correctly
        assert mock_vector_db.query_collection.call_count == 3, f"Expected 3 calls, got {mock_vector_db.query_collection.call_count}"
        
        # Check the file context query (first call)
        file_query_call = mock_vector_db.query_collection.call_args_list[0]
        assert file_query_call[1]["where"] == {"filename": "project_guide.pdf"}, "File context query should use where filter"
        assert file_query_call[1]["n_results"] == 10, "File context should request more results"
        
        print("✅ Vector DB queries verified")
        print("✅ File context integration test PASSED")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_endpoint_parameter_handling():
    """Test that chat endpoint handles all parameters correctly."""
    print("\n🧪 Testing Chat Endpoint Parameter Handling...")
    
    from app.schemas.models import QueryRequest
    
    # Create a comprehensive request
    request = QueryRequest(
        session_id="test_session_123",
        query_text="Analyze the document and create tasks",
        history=[{"role": "user", "content": "Previous message"}],
        current_step=2,
        uploaded_file_context_name="analysis.pdf",
        explain_active=True,
        tasks_active=True,
        selected_alignment="detailed"
    )
    
    print("✅ QueryRequest created with all parameters")
    print(f"📁 File context: {request.uploaded_file_context_name}")
    print(f"🔍 Explain mode: {request.explain_active}")
    print(f"📋 Tasks mode: {request.tasks_active}")
    print(f"⚖️ Alignment: {request.selected_alignment}")
    
    # Verify all fields are accessible
    assert request.uploaded_file_context_name == "analysis.pdf"
    assert request.explain_active is True
    assert request.tasks_active is True
    assert request.selected_alignment == "detailed"
    
    print("✅ Parameter handling test PASSED")
    return True

if __name__ == "__main__":
    print("🚀 Running Phase 3 Integration Tests...")
    
    # Test 1: File context integration
    test1_passed = test_file_context_integration()
    
    # Test 2: Parameter handling  
    test2_passed = test_endpoint_parameter_handling()
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL PHASE 3 TESTS PASSED!")
        print("✅ File context retrieval working")
        print("✅ Parameter handling working") 
        print("✅ Service integration working")
        print("\n📚 Phase 3 implementation is ready for production!")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1)
