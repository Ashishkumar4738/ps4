import logging
from database.connection import get_connection
import json
from documents.document_store import (
    SUMMARY_FILE,
    initialize_store,
    save_summary,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate():
    initialize_store()

    with SUMMARY_FILE.open("r", encoding="utf-8") as file:
        documents = json.load(file)

    if not isinstance(documents, list):
        raise ValueError("summaries.json must contain a list")

    migrated = 0

    for document in documents:
        source_path = document.get("source_path")

        if not source_path:
            logger.warning(
                "Skipping %s: missing source_path",
                document.get("filename", "unknown"),
            )
            continue

        # Migration preserves the stored summary and metadata.
        # It does not require the original source file to exist.


        with get_connection() as connection:
            connection.execute("""
                INSERT INTO documents (
                    document_id, filename, source_path,
                    file_hash, summary, chunk_count,
                    key_points, action_items, status, processed_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_path) DO NOTHING
            """, (
                document["document_id"],
                document["filename"],
                source_path,
                document.get("file_hash", ""),
                document.get("summary", ""),
                document.get("chunk_count", 0),
                json.dumps(document.get("key_points", []), ensure_ascii=False),
                json.dumps(document.get("action_items", []), ensure_ascii=False),
                document.get("status", "processed"),
                document.get("processed_at", ""),
            ))

        migrated += 1

    logger.info("Migration completed; examined %d records", migrated)


if __name__ == "__main__":
    migrate()
