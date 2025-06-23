"""Test Phase 3 Implementation - Document Context in Chat"""
import pytest
from unittest.mock import Mock, patch
from app.services.chat_service import ChatService
from app.services.vector_db_service import VectorDBService
from app.core.config import settings


class TestChatServiceFileContext:
    """Test the enhanced ChatService with file context functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        # Mock VectorDBService
        self.mock_vector_db = Mock(spec=VectorDBService)
        self.chat_service = ChatService(vector_db_service=self.mock_vector_db)
        
    def test_process_query_without_file_context(self):
        """Test normal query processing without file context."""
        # Mock vector DB responses
        self.mock_vector_db.query_collection.side_effect = [
            {"documents": [["Framework info content"]], "metadatas": [[{"filename": "framework.pdf", "chunk_index": 1}]]},
            {"documents": [["User doc content"]], "metadatas": [[{"filename": "user.pdf", "chunk_index": 1}]]}
        ]
        
        # Mock LLM response
        with patch.object(self.chat_service.llm, 'invoke') as mock_llm:
            mock_response = Mock()
            mock_response.content = "AI response"
            mock_llm.return_value = mock_response
            
            with patch('app.prompt_engineering.builder.get_universal_matrix_prompt') as mock_prompt:
                mock_prompt.return_value = Mock()
                
                response, history, step, planner = self.chat_service.process_query(
                    session_id="test_session",
                    query_text="What is agile planning?",
                    api_history_data=[]
                )
                
                assert response == "AI response"
                assert step == 1
                assert len(history) == 2  # Human + AI message
                
                # Verify vector DB was queried for both collections
                assert self.mock_vector_db.query_collection.call_count == 2
    
    def test_process_query_with_file_context(self):
        """Test query processing with specific file context."""
        # Mock vector DB responses - file context query + framework query + reduced user query
        self.mock_vector_db.query_collection.side_effect = [
            {"documents": [["Specific file content"]], "metadatas": [[{"filename": "target.pdf", "chunk_index": 1}]]},  # File context
            {"documents": [["Framework info"]], "metadatas": [[{"filename": "framework.pdf", "chunk_index": 1}]]},  # Framework
            {"documents": [["Other user content"]], "metadatas": [[{"filename": "other.pdf", "chunk_index": 1}]]}  # User docs
        ]
        
        # Mock LLM response
        with patch.object(self.chat_service.llm, 'invoke') as mock_llm:
            mock_response = Mock()
            mock_response.content = "AI response with file context"
            mock_llm.return_value = mock_response
            
            with patch('app.prompt_engineering.builder.get_universal_matrix_prompt') as mock_prompt:
                mock_prompt.return_value = Mock()
                
                response, history, step, planner = self.chat_service.process_query(
                    session_id="test_session",
                    query_text="What does the document say about planning?",
                    api_history_data=[],
                    uploaded_file_context_name="target.pdf"
                )
                
                assert response == "AI response with file context"
                
                # Verify file-specific query was made with where filter
                file_context_call = self.mock_vector_db.query_collection.call_args_list[0]
                assert file_context_call[1]["where"] == {"filename": "target.pdf"}
                assert file_context_call[1]["n_results"] == 10  # More results for file context
    
    def test_process_query_with_file_context_no_results(self):
        """Test query processing when file context returns no results."""
        # Mock vector DB responses - empty file context query
        self.mock_vector_db.query_collection.side_effect = [
            {"documents": [[]], "metadatas": [[]]},  # Empty file context
            {"documents": [["Framework info"]], "metadatas": [[{"filename": "framework.pdf", "chunk_index": 1}]]},  # Framework
            {"documents": [["Other content"]], "metadatas": [[{"filename": "other.pdf", "chunk_index": 1}]]}  # User docs
        ]
        
        # Mock LLM response
        with patch.object(self.chat_service.llm, 'invoke') as mock_llm:
            mock_response = Mock()
            mock_response.content = "AI response"
            mock_llm.return_value = mock_response
            
            with patch('app.prompt_engineering.builder.get_universal_matrix_prompt') as mock_prompt:
                mock_prompt.return_value = Mock()
                
                response, history, step, planner = self.chat_service.process_query(
                    session_id="test_session",
                    query_text="What does the document say?",
                    api_history_data=[],
                    uploaded_file_context_name="nonexistent.pdf"
                )
                
                assert response == "AI response"
                
                # Verify that the context mentions no relevant content found
                prompt_call = mock_prompt.call_args[1]
                assert "No relevant content found" in prompt_call["general_context"]

    def test_process_query_with_all_modes(self):
        """Test query processing with all mode flags enabled."""
        # Mock vector DB responses
        self.mock_vector_db.query_collection.side_effect = [
            {"documents": [["File content"]], "metadatas": [[{"filename": "test.pdf", "chunk_index": 1}]]},
            {"documents": [["Framework info"]], "metadatas": [[{"filename": "framework.pdf", "chunk_index": 1}]]},
            {"documents": [["User content"]], "metadatas": [[{"filename": "user.pdf", "chunk_index": 1}]]}
        ]
        
        # Mock LLM response
        with patch.object(self.chat_service.llm, 'invoke') as mock_llm:
            mock_response = Mock()
            mock_response.content = "Comprehensive AI response"
            mock_llm.return_value = mock_response
            
            with patch('app.prompt_engineering.builder.get_universal_matrix_prompt') as mock_prompt:
                mock_prompt.return_value = Mock()
                
                response, history, step, planner = self.chat_service.process_query(
                    session_id="test_session",
                    query_text="Explain the planning process",
                    api_history_data=[],
                    uploaded_file_context_name="test.pdf",
                    explain_active=True,
                    tasks_active=True,
                    selected_alignment="detailed"
                )
                
                assert response == "Comprehensive AI response"
                
                # Verify that all mode contexts are included
                prompt_call = mock_prompt.call_args[1]
                context = prompt_call["general_context"]
                assert "EXPLAIN MODE ACTIVE" in context
                assert "TASKS MODE ACTIVE" in context
                assert "ALIGNMENT: DETAILED" in context
                assert "File Context from test.pdf" in context


class TestChatEndpoint:
    """Test the chat endpoint integration."""
    
    @pytest.mark.asyncio
    async def test_chat_endpoint_basic(self):
        """Test basic chat endpoint functionality."""
        from app.endpoints.chat import handle_chat_request
        from app.schemas.models import QueryRequest
        
        # Mock the chat service
        with patch('app.endpoints.chat.get_chat_service') as mock_get_service:
            mock_service = Mock()
            mock_service.process_query.return_value = ("AI response", [], 1, None)
            mock_get_service.return_value = mock_service
            
            request = QueryRequest(
                session_id="test_session",
                query_text="Hello",
                history=[],
                current_step=1
            )
            
            response = await handle_chat_request(request, mock_service)
            
            assert response.response == "AI response"
            assert response.current_step == 1
            
            # Verify all parameters were passed
            call_args = mock_service.process_query.call_args
            assert call_args[1]["session_id"] == "test_session"
            assert call_args[1]["query_text"] == "Hello"
            assert call_args[1]["uploaded_file_context_name"] is None
    
    @pytest.mark.asyncio  
    async def test_chat_endpoint_with_file_context(self):
        """Test chat endpoint with file context."""
        from app.endpoints.chat import handle_chat_request
        from app.schemas.models import QueryRequest
        
        with patch('app.endpoints.chat.get_chat_service') as mock_get_service:
            mock_service = Mock()
            mock_service.process_query.return_value = ("File-aware response", [], 1, None)
            mock_get_service.return_value = mock_service
            
            request = QueryRequest(
                session_id="test_session",
                query_text="What does the document say?",
                history=[],
                current_step=1,
                uploaded_file_context_name="document.pdf",
                explain_active=True
            )
            
            response = await handle_chat_request(request, mock_service)
            
            assert response.response == "File-aware response"
            
            # Verify file context was passed
            call_args = mock_service.process_query.call_args
            assert call_args[1]["uploaded_file_context_name"] == "document.pdf"
            assert call_args[1]["explain_active"] is True


if __name__ == "__main__":
    print("Phase 3 tests created. Run with: pytest tests/test_phase3.py -v")
