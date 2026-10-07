
from logger_config import logger

from database.connection import get_connection




def initialize_database():
    """
    Create the database schema if it does not exist.
    """

    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                document_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                source_path TEXT NOT NULL UNIQUE,
                file_hash TEXT NOT NULL,
                summary TEXT NOT NULL,
                chunk_count INTEGER NOT NULL DEFAULT 0,
                key_points TEXT NOT NULL DEFAULT '[]',
                action_items TEXT NOT NULL DEFAULT '[]',
                status TEXT NOT NULL DEFAULT 'processed',
                processed_at TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_documents_file_hash
            ON documents(file_hash)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_documents_filename
            ON documents(filename)
        """)
    
        connection.execute("""
            CREATE TABLE IF NOT EXISTS meetings (
                meeting_id TEXT PRIMARY KEY,
                started_at TEXT NOT NULL,
                ended_at TEXT
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS meeting_segments (
                meeting_id TEXT NOT NULL,
                segment_id INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                text TEXT NOT NULL,
                segment_data TEXT NOT NULL,
                PRIMARY KEY (meeting_id, segment_id),
                FOREIGN KEY (meeting_id)
                    REFERENCES meetings(meeting_id)
                    ON DELETE CASCADE
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_meeting_segments_timestamp
            ON meeting_segments(meeting_id, timestamp)
        """)
        
        connection.execute("""
            CREATE TABLE IF NOT EXISTS conversation_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                meeting_id TEXT,
                event_type TEXT NOT NULL,
                content TEXT,
                tool_name TEXT,
                tool_arguments TEXT,
                created_at TEXT NOT NULL
        );""")
        
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversation_events_conversation
            ON conversation_events (conversation_id, id);
        """)

    logger.info("SQLite database initialized")
