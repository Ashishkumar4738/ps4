import json
import threading
from datetime import datetime

from config.config import MEETING_FILE
from database.connection import get_connection
from database.schema import initialize_database
from logger_config import logger


class MeetingManager:
    def __init__(self):
        initialize_database()

        meeting_start = datetime.now().astimezone()

        self.meeting_data = {
            "meeting_id": meeting_start.strftime("%Y%m%d_%H%M%S"),
            "started_at": meeting_start.isoformat(),
            "segments": [],
        }

        self.lock = threading.Lock()

        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO meetings (meeting_id, started_at, ended_at)
                VALUES (?, ?, NULL)
                """,
                (
                    self.meeting_data["meeting_id"],
                    self.meeting_data["started_at"],
                ),
            )

        logger.info(
            "Meeting created in SQLite: %s",
            self.meeting_data["meeting_id"],
        )

    def add_segment(self, segment):
        segment = dict(segment)

        with self.lock:
            with get_connection() as connection:
                connection.execute(
                    """
                    INSERT INTO meeting_segments (
                        meeting_id,
                        segment_id,
                        timestamp,
                        text,
                        segment_data
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        self.meeting_data["meeting_id"],
                        segment["segment_id"],
                        segment["timestamp"],
                        segment["text"],
                        json.dumps(segment, ensure_ascii=False),
                    ),
                )

            self.meeting_data["segments"].append(segment)
            self.meeting_data["segments"].sort(
                key=lambda item: item["segment_id"]
            )

        logger.debug(
            "Saved transcript segment %s",
            segment["segment_id"],
        )

    def save(self):
        # Transcript data is written to SQLite by add_segment().
        # Kept for compatibility with existing callers.
        logger.debug("Meeting data is persisted in SQLite")

    def finish(self):
        with self.lock:
            ended_at = datetime.now().astimezone().isoformat()

            with get_connection() as connection:
                connection.execute(
                    """
                    UPDATE meetings
                    SET ended_at = ?
                    WHERE meeting_id = ?
                    """,
                    (
                        ended_at,
                        self.meeting_data["meeting_id"],
                    ),
                )

            self.meeting_data["ended_at"] = ended_at

        logger.info(
            "Meeting finished: %s",
            self.meeting_data["meeting_id"],
        )

    def get_segment_count(self):
        with self.lock:
            return len(self.meeting_data["segments"])

    @property
    def file_path(self):
        from config.config import DATABASE_FILE
        return str(DATABASE_FILE)
