"""
Supabase SQL Migration for Chat Sessions Table
Run this in your Supabase SQL editor to create the chat_sessions table
"""

CREATE_CHAT_SESSIONS_TABLE = """
-- Create chat_sessions table for persistent session storage
CREATE TABLE IF NOT EXISTS chat_sessions (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    conversation_history JSONB DEFAULT '[]'::jsonb,
    current_step INTEGER DEFAULT 1,
    planner_details TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on session_id for fast lookups
CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_id ON chat_sessions(session_id);

-- Create index on last_accessed for cleanup operations
CREATE INDEX IF NOT EXISTS idx_chat_sessions_last_accessed ON chat_sessions(last_accessed);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
DROP TRIGGER IF EXISTS update_chat_sessions_updated_at ON chat_sessions;
CREATE TRIGGER update_chat_sessions_updated_at
    BEFORE UPDATE ON chat_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS) if needed
-- ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;

-- Example RLS policy for authenticated users (uncomment if using Supabase auth)
-- CREATE POLICY "Users can access their own sessions" ON chat_sessions
--     FOR ALL USING (auth.uid()::text = session_id OR session_id LIKE auth.uid()::text || '_%');

COMMENT ON TABLE chat_sessions IS 'Stores persistent chat session state for scalable multi-user support';
COMMENT ON COLUMN chat_sessions.session_id IS 'Unique identifier for chat session, typically UUID or user_id based';
COMMENT ON COLUMN chat_sessions.conversation_history IS 'Serialized conversation messages in JSON format';
COMMENT ON COLUMN chat_sessions.current_step IS 'Current step in the VINO process (1-6)';
COMMENT ON COLUMN chat_sessions.planner_details IS 'Current planner state information';
COMMENT ON COLUMN chat_sessions.last_accessed IS 'Timestamp of last session access for cleanup purposes';
"""

CLEANUP_OLD_SESSIONS_FUNCTION = """
-- Function to clean up old sessions (can be called manually or via cron)
CREATE OR REPLACE FUNCTION cleanup_old_chat_sessions(days_threshold INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM chat_sessions 
    WHERE last_accessed < NOW() - INTERVAL '1 day' * days_threshold;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_old_chat_sessions IS 'Deletes chat sessions older than specified days (default 30)';
"""

if __name__ == "__main__":
    print("=== Chat Sessions Table Migration ===")
    print("Copy and run the following SQL in your Supabase SQL editor:")
    print("\n-- Step 1: Create table and indexes")
    print(CREATE_CHAT_SESSIONS_TABLE)
    print("\n-- Step 2: Create cleanup function")
    print(CLEANUP_OLD_SESSIONS_FUNCTION)
    print("\n=== Migration Complete ===")
    print("\nOptional: Set up a cron job to run cleanup_old_chat_sessions() periodically")
    print("Example: SELECT cleanup_old_chat_sessions(30); -- Delete sessions older than 30 days")
