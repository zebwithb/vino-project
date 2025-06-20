"""Session Storage Service - Handles persistent chat session state."""
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from app.core.config import settings
from app.services.supabase_service import SupabaseService


class SessionStorageService:
    """Service for managing persistent chat session state."""
    
    def __init__(self, supabase_service: Optional[SupabaseService] = None):
        """Initialize with optional Supabase service."""
        self.supabase_service = supabase_service or SupabaseService()
        self.table_name = "chat_sessions"
        
    def get_session_data(self, session_id: str) -> Tuple[List[BaseMessage], int, Optional[str]]:
        """
        Retrieve session data from persistent storage.
        
        Args:
            session_id: Unique identifier for the chat session
            
        Returns:
            Tuple of (conversation_history, current_step, planner_details)
        """
        if not self.supabase_service.client:
            # Fallback to default values if Supabase not available
            return [], 1, None
            
        try:
            # Query the chat_sessions table
            result = self.supabase_service.client.table(self.table_name).select("*").eq("session_id", session_id).execute()
            
            if result.data:
                session_data = result.data[0]
                
                # Convert stored history back to LangChain messages
                history = self._deserialize_history(session_data.get("conversation_history", []))
                step = session_data.get("current_step", 1)
                planner = session_data.get("planner_details")
                
                # Update last_accessed timestamp
                self._update_last_accessed(session_id)
                
                return history, step, planner
            else:
                # Create new session with default values
                return self._create_new_session(session_id)
                
        except Exception as e:
            print(f"Error retrieving session data for {session_id}: {e}")
            # Return defaults on error
            return [], 1, None
    
    def update_session_data(self, session_id: str, history: List[BaseMessage], step: int, planner: Optional[str]) -> bool:
        """
        Update session data in persistent storage.
        
        Args:
            session_id: Unique identifier for the chat session
            history: List of conversation messages
            step: Current process step
            planner: Current planner state
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.supabase_service.client:
            print("Warning: Session state not persisted - Supabase not available")
            return False
            
        try:
            # Serialize the conversation history
            serialized_history = self._serialize_history(history)
            
            session_data = {
                "session_id": session_id,
                "conversation_history": serialized_history,
                "current_step": step,
                "planner_details": planner,
                "last_accessed": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Upsert the session data
            result = self.supabase_service.client.table(self.table_name).upsert(session_data).execute()
            
            if result.data:
                return True
            else:
                print(f"Failed to update session data for {session_id}")
                return False
                
        except Exception as e:
            print(f"Error updating session data for {session_id}: {e}")
            return False
    
    def _create_new_session(self, session_id: str) -> Tuple[List[BaseMessage], int, Optional[str]]:
        """Create a new session with default values."""
        try:
            session_data = {
                "session_id": session_id,
                "conversation_history": [],
                "current_step": 1,
                "planner_details": None,
                "created_at": datetime.utcnow().isoformat(),
                "last_accessed": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            self.supabase_service.client.table(self.table_name).insert(session_data).execute()
            print(f"Created new session: {session_id}")
            
        except Exception as e:
            print(f"Error creating new session {session_id}: {e}")
        
        return [], 1, None
    
    def _update_last_accessed(self, session_id: str) -> None:
        """Update the last_accessed timestamp for a session."""
        try:
            self.supabase_service.client.table(self.table_name).update({
                "last_accessed": datetime.utcnow().isoformat()
            }).eq("session_id", session_id).execute()
        except Exception as e:
            print(f"Error updating last_accessed for {session_id}: {e}")
    
    def _serialize_history(self, history: List[BaseMessage]) -> List[Dict[str, Any]]:
        """Convert LangChain messages to serializable format."""
        serialized = []
        for msg in history:
            if isinstance(msg, HumanMessage):
                serialized.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                serialized.append({"role": "assistant", "content": msg.content})
            elif isinstance(msg, SystemMessage):
                serialized.append({"role": "system", "content": msg.content})
        return serialized
    
    def _deserialize_history(self, serialized_history: List[Dict[str, Any]]) -> List[BaseMessage]:
        """Convert serialized format back to LangChain messages."""
        history = []
        for item in serialized_history:
            role = item.get("role")
            content = item.get("content", "")
            if role == "user":
                history.append(HumanMessage(content=content))
            elif role == "assistant":
                history.append(AIMessage(content=content))
            elif role == "system":
                history.append(SystemMessage(content=content))
        return history
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session from storage.
        
        Args:
            session_id: Session to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.supabase_service.client:
            return False
            
        try:
            result = self.supabase_service.client.table(self.table_name).delete().eq("session_id", session_id).execute()
            return bool(result.data)
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False
    
    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """
        Clean up sessions older than specified days.
        
        Args:
            days_old: Delete sessions not accessed for this many days
            
        Returns:
            int: Number of sessions deleted
        """
        if not self.supabase_service.client:
            return 0
            
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days_old)).isoformat()
            
            result = self.supabase_service.client.table(self.table_name).delete().lt("last_accessed", cutoff_date).execute()
            
            deleted_count = len(result.data) if result.data else 0
            if deleted_count > 0:
                print(f"Cleaned up {deleted_count} old sessions (older than {days_old} days)")
            
            return deleted_count
            
        except Exception as e:
            print(f"Error cleaning up old sessions: {e}")
            return 0
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session metadata without loading full conversation history.
        
        Args:
            session_id: Session to query
            
        Returns:
            Dict with session metadata or None if not found
        """
        if not self.supabase_service.client:
            return None
            
        try:
            result = self.supabase_service.client.table(self.table_name).select(
                "session_id, current_step, planner_details, created_at, last_accessed, updated_at"
            ).eq("session_id", session_id).execute()
            
            if result.data:
                return result.data[0]
            else:
                return None
                
        except Exception as e:
            print(f"Error getting session info for {session_id}: {e}")
            return None
