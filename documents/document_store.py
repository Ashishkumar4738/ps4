import hashlib
import json
import logging

from datetime import datetime
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent

LIBRARY_DIR = PROJECT_DIR / "document_library"
SUMMARY_FILE = LIBRARY_DIR / "summaries.json"

logger = logging.getLogger(__name__)


# ============================================================
# Initialization
# ============================================================

def initialize_store():
    """
    Create the library directory and JSON file if missing.
    """

    LIBRARY_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if not SUMMARY_FILE.exists():
        save_all_documents([])

    logger.info("Document store initialized")


# ============================================================
# Internal JSON helpers
# ============================================================

def load_all_documents():
    """
    Load all document records from JSON.
    """

    initialize_store()

    try:
        with SUMMARY_FILE.open(
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError(
                "Document store must contain a JSON list."
            )

        return data

    except json.JSONDecodeError as exc:
        logger.exception(
            "Document store JSON is invalid"
        )
        raise RuntimeError(
            f"Cannot read document store: {SUMMARY_FILE}"
        ) from exc


def save_all_documents(documents):
    """
    Write document records to JSON atomically.
    """

    LIBRARY_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    temporary_file = SUMMARY_FILE.with_suffix(
        ".tmp"
    )

    with temporary_file.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            documents,
            file,
            ensure_ascii=False,
            indent=2
        )

    temporary_file.replace(SUMMARY_FILE)


# ============================================================
# Helpers
# ============================================================

def calculate_file_hash(filename):
    """
    Calculate SHA-256 of a file.
    """

    path = Path(filename).expanduser().resolve()
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b""
        ):
            digest.update(chunk)

    return digest.hexdigest()


def find_document(query):
    """
    Find documents by filename or document ID.

    Exact matches are preferred. If multiple records match
    loosely, return all matches to avoid guessing.
    """

    query = query.strip()

    if not query:
        return []

    documents = load_all_documents()
    normalized_query = query.casefold()

    # Exact filename or ID match.
    exact_matches = [
        document
        for document in documents
        if (
            document.get("filename", "").casefold()
            == normalized_query
            or document.get("document_id")
            == query
        )
    ]

    if exact_matches:
        return exact_matches

    # Allow a name without its extension.
    stem_matches = [
        document
        for document in documents
        if (
            Path(
                document.get("filename", "")
            ).stem.casefold()
            == normalized_query
        )
    ]

    if stem_matches:
        return stem_matches

    # Partial matching for natural voice queries.
    partial_matches = [
        document
        for document in documents
        if normalized_query
        in document.get("filename", "").casefold()
    ]

    return partial_matches


# ============================================================
# Save or update
# ============================================================

def save_summary(
    filename,
    summary,
    file_hash=None,
    chunk_count=0,
    key_points=None,
    action_items=None
):
    """
    Save a document summary.

    Existing records with the same source path are updated.
    """

    path = Path(filename).expanduser().resolve()

    if not path.is_file():
        raise FileNotFoundError(
            f"Source document not found: {path}"
        )

    if not summary or not summary.strip():
        raise ValueError(
            "Cannot save an empty summary."
        )

    if file_hash is None:
        file_hash = calculate_file_hash(path)

    documents = load_all_documents()
    now = datetime.now().astimezone().isoformat(
        timespec="seconds"
    )

    # Use the source path to distinguish files with
    # identical filenames in different directories.
    existing = next(
        (
            document
            for document in documents
            if document.get("source_path") == str(path)
        ),
        None
    )

    if existing:
        existing.update({
            "filename": path.name,
            "file_hash": file_hash,
            "summary": summary,
            "chunk_count": chunk_count,
            "key_points": key_points or [],
            "action_items": action_items or [],
            "status": "processed",
            "processed_at": now,
        })

        record = existing

    else:
        record = {
            "document_id": file_hash[:16],
            "filename": path.name,
            "source_path": str(path),
            "file_hash": file_hash,
            "summary": summary,
            "chunk_count": chunk_count,
            "key_points": key_points or [],
            "action_items": action_items or [],
            "status": "processed",
            "processed_at": now,
        }

        documents.append(record)

    save_all_documents(documents)

    logger.info(
        "Saved summary for %s",
        path.name
    )

    return record


# ============================================================
# List documents
# ============================================================

def list_documents():
    """
    Return a compact list of saved document records.
    """

    documents = load_all_documents()

    return [
        {
            "document_id": document.get("document_id"),
            "filename": document.get("filename"),
            "status": document.get("status"),
            "processed_at": document.get("processed_at"),
        }
        for document in documents
    ]


# ============================================================
# Duplicate detection
# ============================================================

def find_by_hash(file_hash):
    """
    Find documents with identical file content.
    """

    documents = load_all_documents()

    return [
        document
        for document in documents
        if document.get("file_hash") == file_hash
    ]


# ============================================================
# Remove document
# ============================================================

def remove_document(document_id):
    """
    Remove a record from the summary library.
    Does not delete the original document.
    """

    documents = load_all_documents()

    remaining = [
        document
        for document in documents
        if document.get("document_id") != document_id
    ]

    if len(remaining) == len(documents):
        return False

    save_all_documents(remaining)

    logger.info(
        "Removed document record %s",
        document_id
    )

    return True
