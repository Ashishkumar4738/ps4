
import hashlib
import json
import logging

from datetime import datetime
from pathlib import Path
import uuid

from config.config import PROJECT_DIR
from database.connection import get_connection
from database.schema import initialize_database

logger = logging.getLogger(__name__)

LIBRARY_DIR = PROJECT_DIR / "document_library"
SUMMARY_FILE = LIBRARY_DIR / "summaries.json"


# ============================================================
# Initialization
# ============================================================

def initialize_store():
    """
    Initialize SQLite and ensure the legacy JSON file exists.
    """

    LIBRARY_DIR.mkdir(parents=True, exist_ok=True)

    if not SUMMARY_FILE.exists():
        SUMMARY_FILE.write_text("[]", encoding="utf-8")

    initialize_database()
    logger.info("Document store initialized")


# ============================================================
# JSON serialization helpers
# ============================================================

def _serialize_list(value):
    return json.dumps(value or [], ensure_ascii=False)


def _deserialize_document(row):
    if row is None:
        return None

    document = dict(row)

    document["key_points"] = json.loads(
        document["key_points"]
    )
    document["action_items"] = json.loads(
        document["action_items"]
    )

    return document


# ============================================================
# Legacy JSON helpers
# ============================================================

def load_all_documents():
    """
    Return all documents from SQLite as Python dictionaries.
    Keeps the previous function interface.
    """

    initialize_store()

    with get_connection() as connection:
        rows = connection.execute("""
            SELECT *
            FROM documents
            ORDER BY processed_at DESC
        """).fetchall()

    return [
        _deserialize_document(row)
        for row in rows
    ]


# ============================================================
# Helpers
# ============================================================

def calculate_file_hash(filename):
    """Calculate the SHA-256 hash of a file."""

    path = Path(filename).expanduser().resolve()
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def find_document(query):
    """
    Find documents by ID or filename.
    Exact matches take precedence over partial matches.
    """

    query = query.strip()

    if not query:
        return []

    documents = load_all_documents()
    normalized_query = query.casefold()

    exact_matches = [
        document for document in documents
        if (
            document["filename"].casefold() == normalized_query
            or document["document_id"] == query
        )
    ]

    if exact_matches:
        return exact_matches

    stem_matches = [
        document for document in documents
        if Path(document["filename"]).stem.casefold()
        == normalized_query
    ]

    if stem_matches:
        return stem_matches

    return [
        document for document in documents
        if normalized_query in document["filename"].casefold()
    ]


# ============================================================
# Save or update
# ============================================================

def save_summary(
    filename,
    summary,
    file_hash=None,
    chunk_count=0,
    key_points=None,
    action_items=None,
):
    """Save a document summary in SQLite."""

    path = Path(filename).expanduser().resolve()

    if not path.is_file():
        raise FileNotFoundError(
            f"Source document not found: {path}"
        )

    if not summary or not summary.strip():
        raise ValueError("Cannot save an empty summary.")

    if file_hash is None:
        file_hash = calculate_file_hash(path)

    now = datetime.now().astimezone().isoformat(
        timespec="seconds"
    )

    # Keep the same ID when updating an existing source path.
    with get_connection() as connection:
        existing = connection.execute("""
            SELECT document_id
            FROM documents
            WHERE source_path = ?
        """, (str(path),)).fetchone()


        document_id = (
            existing["document_id"]
            if existing
            else uuid.uuid4().hex
        )


        connection.execute("""
            INSERT INTO documents (
                document_id,
                filename,
                source_path,
                file_hash,
                summary,
                chunk_count,
                key_points,
                action_items,
                status,
                processed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(source_path) DO UPDATE SET
                filename = excluded.filename,
                file_hash = excluded.file_hash,
                summary = excluded.summary,
                chunk_count = excluded.chunk_count,
                key_points = excluded.key_points,
                action_items = excluded.action_items,
                status = excluded.status,
                processed_at = excluded.processed_at
        """, (
            document_id,
            path.name,
            str(path),
            file_hash,
            summary,
            chunk_count,
            _serialize_list(key_points),
            _serialize_list(action_items),
            "processed",
            now,
        ))

        row = connection.execute("""
            SELECT *
            FROM documents
            WHERE source_path = ?
        """, (str(path),)).fetchone()

    logger.info("Saved summary for %s", path.name)

    return _deserialize_document(row)


# ============================================================
# List documents
# ============================================================

def list_documents():
    """Return compact document records."""

    return [
        {
            "document_id": document["document_id"],
            "filename": document["filename"],
            "status": document["status"],
            "processed_at": document["processed_at"],
        }
        for document in load_all_documents()
    ]


# ============================================================
# Duplicate detection
# ============================================================

def find_by_hash(file_hash):
    """Find documents with identical file content."""

    with get_connection() as connection:
        rows = connection.execute("""
            SELECT *
            FROM documents
            WHERE file_hash = ?
        """, (file_hash,)).fetchall()

    return [
        _deserialize_document(row)
        for row in rows
    ]


# ============================================================
# Remove document
# ============================================================

def remove_document(document_id):
    """Remove a database record, not the original file."""

    with get_connection() as connection:
        cursor = connection.execute("""
            DELETE FROM documents
            WHERE document_id = ?
        """, (document_id,))

    if cursor.rowcount == 0:
        return False

    logger.info("Removed document record %s", document_id)
    return True
