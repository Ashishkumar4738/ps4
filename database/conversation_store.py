
import json
from logger_config import logger
from datetime import datetime

from database.connection import get_connection
from database.schema import initialize_database




def log_conversation_event(
    conversation_id,
    event_type,
    content=None,
    meeting_id=None,
    tool_name=None,
    tool_arguments=None,
):
    """Save a user command, LLM response, or tool event to SQLite."""

    try:
        timestamp = datetime.now().astimezone().isoformat()

        if tool_arguments is not None:
            tool_arguments = json.dumps(
                tool_arguments,
                ensure_ascii=False,
                default=str,
            )

        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO conversation_events (
                    conversation_id,
                    meeting_id,
                    event_type,
                    content,
                    tool_name,
                    tool_arguments,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    conversation_id,
                    meeting_id,
                    event_type,
                    content,
                    tool_name,
                    tool_arguments,
                    timestamp,
                ),
            )

        logger.debug(
            "Conversation event saved: %s",
            event_type,
        )

    except Exception:
        logger.exception("Failed to save conversation event")
