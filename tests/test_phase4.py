"""Test Phase 4 Implementation - Session Storage"""
import pytest
from unittest.mock import Mock, patch
from langchain_core.messages import HumanMessage, AIMessage

from app.services.session_storage_service import SessionStorageService
from app.services.chat_service import ChatService
from app.services.supabase_service import SupabaseService


class TestSessionStorageService:
    """Test the SessionStorageService functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.mock_supabase = Mock(spec=SupabaseService)
        self.mock_client = Mock()
        self.mock_supabase.client = self.mock_client
        self.session_storage = SessionStorageService(supabase_service=self.mock_supabase)
        
    def test_get_new_session_data(self):
        """Test retrieving data for a new session."""
        # Mock empty result for new session
        mock_table = Mock()
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[])
        self.mock_client.table.return_value = mock_table
        
        # Mock session creation
        mock_insert_table = Mock()
        mock_insert_table.insert.return_value = mock_insert_table
        mock_insert_table.execute.return_value = Mock(data=[{"session_id": "test_session"}])
        
        # Need to return different mocks for different table calls
        self.mock_client.table.side_effect = [mock_table, mock_insert_table]
        
        history, step, planner = self.session_storage.get_session_data("test_session")
        
        assert history == []
        assert step == 1
        assert planner is None
        
        # Verify session creation was attempted
        self.mock_client.table.assert_called_with("chat_sessions")
    
    def test_get_existing_session_data(self):
        """Test retrieving data for an existing session."""
        # Mock existing session data
        session_data = {
            "session_id": "existing_session",
            "conversation_history": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ],
            "current_step": 2,
            "planner_details": "Test planner"
        }
        
        mock_table = Mock()
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[session_data])
        self.mock_client.table.return_value = mock_table
        
        # Mock update last_accessed call
        mock_update_table = Mock()
        mock_update_table.update.return_value = mock_update_table
        mock_update_table.eq.return_value = mock_update_table
        mock_update_table.execute.return_value = Mock()
        
        self.mock_client.table.side_effect = [mock_table, mock_update_table]
        
        history, step, planner = self.session_storage.get_session_data("existing_session")
        
        assert len(history) == 2
        assert isinstance(history[0], HumanMessage)
        assert isinstance(history[1], AIMessage)
        assert history[0].content == "Hello"
        assert history[1].content == "Hi there!"
        assert step == 2
        assert planner == "Test planner"
    
    def test_update_session_data(self):
        """Test updating session data."""
        history = [
            HumanMessage(content="Test message"),
            AIMessage(content="Test response")
        ]
        
        mock_table = Mock()
        mock_table.upsert.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[{"session_id": "test_session"}])
        self.mock_client.table.return_value = mock_table
        
        success = self.session_storage.update_session_data("test_session", history, 3, "test_planner")
        
        assert success is True
        
        # Verify upsert was called with correct data
        call_args = mock_table.upsert.call_args[0][0]
        assert call_args["session_id"] == "test_session"
        assert call_args["current_step"] == 3
        assert call_args["planner_details"] == "test_planner"
        assert len(call_args["conversation_history"]) == 2
        assert call_args["conversation_history"][0]["role"] == "user"
        assert call_args["conversation_history"][1]["role"] == "assistant"
    
    def test_cleanup_old_sessions(self):
        """Test cleaning up old sessions."""
        mock_table = Mock()
        mock_table.delete.return_value = mock_table
        mock_table.lt.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[{"id": 1}, {"id": 2}])  # 2 deleted sessions
        self.mock_client.table.return_value = mock_table
        
        deleted_count = self.session_storage.cleanup_old_sessions(days_old=7)
        
        assert deleted_count == 2
        mock_table.delete.assert_called_once()
        mock_table.lt.assert_called_once()
    
    def test_session_storage_without_supabase(self):
        """Test graceful degradation when Supabase is not available."""
        session_storage = SessionStorageService(supabase_service=None)
        
        # Should return defaults without errors
        history, step, planner = session_storage.get_session_data("test_session")
        assert history == []
        assert step == 1
        assert planner is None
        
        # Update should return False but not error
        success = session_storage.update_session_data("test_session", [], 1, None)
        assert success is False


class TestChatServiceWithSessionStorage:
    """Test ChatService integration with SessionStorageService."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.mock_vector_db = Mock()
        self.mock_session_storage = Mock(spec=SessionStorageService)
        self.chat_service = ChatService(
            vector_db_service=self.mock_vector_db,
            session_storage_service=self.mock_session_storage
        )
    
    def test_get_session_data_from_persistent_storage(self):
        """Test that session data is loaded from persistent storage."""
        # Mock session storage response
        test_history = [HumanMessage(content="Previous message")]
        self.mock_session_storage.get_session_data.return_value = (test_history, 2, "test_planner")
        
        history, step, planner = self.chat_service._get_session_data("test_session")
        
        assert history == test_history
        assert step == 2
        assert planner == "test_planner"
        self.mock_session_storage.get_session_data.assert_called_once_with("test_session")
    
    def test_fallback_to_memory_on_storage_error(self):
        """Test fallback to memory when persistent storage fails."""
        # Mock storage service to raise an exception
        self.mock_session_storage.get_session_data.side_effect = Exception("Storage error")
        
        # Should fallback to memory without crashing
        history, step, planner = self.chat_service._get_session_data("test_session")
        
        assert history == []
        assert step == 1
        assert planner is None
        
        # Verify it was stored in memory
        assert "test_session" in self.chat_service.conversation_history
    
    def test_update_session_data_to_persistent_storage(self):
        """Test that session data is saved to persistent storage."""
        test_history = [HumanMessage(content="Test message")]
        self.mock_session_storage.update_session_data.return_value = True
        
        self.chat_service._update_session_data("test_session", test_history, 3, "planner")
        
        self.mock_session_storage.update_session_data.assert_called_once_with(
            "test_session", test_history, 3, "planner"
        )
        
        # Should not store in memory when persistent storage succeeds
        assert "test_session" not in self.chat_service.conversation_history
    
    def test_fallback_to_memory_on_update_error(self):
        """Test fallback to memory when persistent storage update fails."""
        test_history = [HumanMessage(content="Test message")]
        self.mock_session_storage.update_session_data.return_value = False
        
        self.chat_service._update_session_data("test_session", test_history, 3, "planner")
        
        # Should store in memory as fallback
        assert self.chat_service.conversation_history["test_session"] == test_history
        assert self.chat_service.current_process_step["test_session"] == 3
        assert self.chat_service.planner_details["test_session"] == "planner"
    
    def test_delete_session(self):
        """Test session deletion."""
        # Setup some memory state
        self.chat_service.conversation_history["test_session"] = [HumanMessage(content="test")]
        self.chat_service.current_process_step["test_session"] = 2
        self.chat_service.planner_details["test_session"] = "planner"
        
        self.mock_session_storage.delete_session.return_value = True
        
        success = self.chat_service.delete_session("test_session")
        
        assert success is True
        
        # Verify memory cleanup
        assert "test_session" not in self.chat_service.conversation_history
        assert "test_session" not in self.chat_service.current_process_step
        assert "test_session" not in self.chat_service.planner_details
    
    def test_get_session_info(self):
        """Test getting session information."""
        session_info = {
            "session_id": "test_session",
            "current_step": 2,
            "planner_details": "test_planner",
            "created_at": "2024-01-01T00:00:00Z"
        }
        self.mock_session_storage.get_session_info.return_value = session_info
        
        result = self.chat_service.get_session_info("test_session")
        
        assert result == session_info
        self.mock_session_storage.get_session_info.assert_called_once_with("test_session")


class TestSessionStorageIntegration:
    """Integration tests for the complete session storage system."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_session_persistence(self):
        """Test complete session persistence flow."""
        from app.endpoints.chat import handle_chat_request
        from app.schemas.models import QueryRequest
        
        # Mock the dependencies
        with patch('app.endpoints.chat.get_chat_service') as mock_get_service:
            mock_chat_service = Mock()
            mock_chat_service.process_query.return_value = ("Response", [], 2, "planner")
            mock_get_service.return_value = mock_chat_service
            
            request = QueryRequest(
                session_id="persistent_session",
                query_text="Test message",
                history=[],
                current_step=1
            )
            
            response = await handle_chat_request(request, mock_chat_service)
            
            # Verify the service was called with persistent session ID
            call_args = mock_chat_service.process_query.call_args
            assert call_args[1]["session_id"] == "persistent_session"
            
            # Verify response
            assert response.response == "Response"
            assert response.current_step == 2


if __name__ == "__main__":
    print("Phase 4 tests created. Run with: pytest tests/test_phase4.py -v")
    print("\nTest coverage includes:")
    print("✅ SessionStorageService with Supabase backend")
    print("✅ ChatService integration with persistent storage")
    print("✅ Fallback to memory when storage unavailable")
    print("✅ Session CRUD operations")
    print("✅ Cleanup functionality")
    print("✅ End-to-end integration")
