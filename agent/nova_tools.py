import json
from datetime import datetime, timedelta
from pathlib import Path
from logger_config import logger
from database.connection import get_connection
from documents.document_store import (
    list_documents,
    find_document,
)
# ============================================================
# Configuration
# ============================================================

MEETING_FILE = Path(__file__).resolve().parent.parent /"meetings" / "meeting.json"


# ============================================================
# Internal helpers
# ============================================================


def load_meeting():
    """
    Load the latest meeting and its transcript from SQLite.
    """

    with get_connection() as connection:
        meeting_row = connection.execute("""
            SELECT meeting_id, started_at, ended_at
            FROM meetings
            ORDER BY started_at DESC
            LIMIT 1
        """).fetchone()

        if meeting_row is None:
            logger.error("No meetings found in SQLite")
            raise FileNotFoundError(
                "No meetings found in the SQLite database"
            )

        segment_rows = connection.execute("""
            SELECT segment_data
            FROM meeting_segments
            WHERE meeting_id = ?
            ORDER BY segment_id
        """, (
            meeting_row["meeting_id"],
        )).fetchall()

    return {
        "meeting_id": meeting_row["meeting_id"],
        "started_at": meeting_row["started_at"],
        "ended_at": meeting_row["ended_at"],
        "segments": [
            json.loads(row["segment_data"])
            for row in segment_rows
        ],
    }



def parse_timestamp(timestamp):
    """Convert ISO timestamp string to datetime."""
    return datetime.fromisoformat(timestamp)


def get_segment_end(segment):
    """Calculate the end time of a transcript segment."""
    start = parse_timestamp(segment["timestamp"])
    duration = float(segment.get("duration_seconds", 0))

    return start + timedelta(seconds=duration)


def segment_overlaps(segment, start_time, end_time):
    """
    Return True if a transcript segment overlaps
    the requested time range.
    """

    segment_start = parse_timestamp(segment["timestamp"])
    segment_end = get_segment_end(segment)

    return (
        segment_start < end_time
        and segment_end > start_time
    )


# ============================================================
# Tool 1: Get transcript between two timestamps
# ============================================================

def get_transcript_between(start_time, end_time):
    """
    Get all transcript segments that overlap a given
    time range.

    Example:

        get_transcript_between(
            "2026-09-25T15:44:30",
            "2026-09-25T15:45:00"
        )
    """

    meeting = load_meeting()

    start = parse_timestamp(start_time)
    end = parse_timestamp(end_time)

    if start >= end:
        logger.error("start_time must be before end_time")
        raise ValueError("start_time must be before end_time")

    results = []

    for segment in meeting.get("segments", []):

        if segment_overlaps(segment, start, end):
            results.append(segment)

    return {
        "meeting_id": meeting.get("meeting_id"),
        "start_time": start_time,
        "end_time": end_time,
        "segment_count": len(results),
        "segments": results
    }


# ============================================================
# Tool 2: Get recent transcript
# ============================================================

def summarize_meeting(minutes):
    """
    Get transcript from the most recent `minutes`.

    Example:

        summarize_meeting(10)
    """

    meeting = load_meeting()

    if minutes <= 0:
        logger.error("minutes must be greater than zero")
        raise ValueError("minutes must be greater than zero")

    segments = meeting.get("segments", [])

    if not segments:
        return {
            "meeting_id": meeting.get("meeting_id"),
            "segment_count": 0,
            "segments": []
        }

    # Use the latest segment timestamp as the reference point.
    latest_segment = max(
        segments,
        key=lambda x: parse_timestamp(x["timestamp"])
    )

    latest_time = parse_timestamp(latest_segment["timestamp"])

    start_time = latest_time - timedelta(minutes=minutes)

    results = []

    for segment in segments:

        segment_time = parse_timestamp(segment["timestamp"])

        if segment_time >= start_time:
            results.append(segment)

    return {
        "meeting_id": meeting.get("meeting_id"),
        "start_time": start_time.isoformat(),
        "end_time": latest_time.isoformat(),
        "segment_count": len(results),
        "segments": results
    }


# ============================================================
# Tool 3: Search meeting
# ============================================================

def search_meeting(query):
    """
    Search the meeting transcript for a keyword or phrase.

    Example:

        search_meeting("database")
    """

    meeting = load_meeting()

    query = query.strip().lower()

    if not query:
        logger.error("Search query cannot be empty")
        raise ValueError("Search query cannot be empty")

    results = []

    for segment in meeting.get("segments", []):

        text = segment.get("text", "")

        if query in text.lower():
            results.append(segment)

    return {
        "meeting_id": meeting.get("meeting_id"),
        "query": query,
        "match_count": len(results),
        "segments": results
    }


# ============================================================
# Helper: Convert segments to plain text
# ============================================================

def segments_to_text(segments):
    """
    Convert transcript segments into clean text
    suitable for sending to an LLM.
    """

    lines = []

    for segment in segments:

        timestamp = segment.get("timestamp", "")
        text = segment.get("text", "").strip()

        if text:
            lines.append(
                f"[{timestamp}] {text}"
            )

    return "\n".join(lines)


# ============================================================
# Document Library Tools
# ============================================================

def list_saved_documents():
    """List documents processed and saved in Nova's library."""
    documents = list_documents()

    return {
        "document_count": len(documents),
        "documents": [
            {
                "document_id": doc.get("document_id"),
                "filename": doc.get("filename"),
                "status": doc.get("status"),
                "processed_at": doc.get("processed_at"),
            }
            for doc in documents
        ],
    }



def get_document_summary(query):
    """Retrieve a saved document summary by filename or name."""
    query = query.strip()

    if not query:
        raise ValueError("Document name cannot be empty.")

    matches = find_document(query)

    if not matches:
        return {
            "found": False,
            "query": query,
            "message": (
                "No matching document exists in the saved "
                "document library."
            ),
        }

    if len(matches) > 1:
        return {
            "found": False,
            "query": query,
            "message": "Multiple documents matched.",
            "matches": [
                doc.get("filename")
                for doc in matches
            ],
        }

    document = matches[0]

    return {
        "found": True,
        "source": "saved_document_library",
        "filename": document.get("filename"),
        "summary": document.get("summary", ""),
        "key_points": document.get("key_points", []),
        "action_items": document.get("action_items", []),
        "note": (
            "The summary may contain an Action Items section. "
            "Use the saved summary as the source of truth. "
            "Do not substitute meeting transcript information."
        ),
    }



def search_saved_documents(query):
    """Search the document library by filename."""
    query = query.strip().lower()

    if not query:
        raise ValueError("Search query cannot be empty.")

    documents = list_documents()

    matches = [
        {
            "document_id": doc.get("document_id"),
            "filename": doc.get("filename"),
            "status": doc.get("status"),
            "summary_preview": (
                doc.get("summary", "")[:300]
            ),
        }
        for doc in documents
        if query in doc.get("filename", "").lower()
    ]

    return {
        "query": query,
        "match_count": len(matches),
        "documents": matches,
    }
# ============================================================
# Simple local test
# ============================================================

# if __name__ == "__main__":

    print("\n=== Nova Tools Test ===\n")

    meeting = load_meeting()

    print("Meeting ID:")
    print(meeting.get("meeting_id"))

    print("\nTotal segments:")
    print(len(meeting.get("segments", [])))

    print("\n--- Recent transcript (5 minutes) ---")

    recent = summarize_meeting(5)

    print(
        segments_to_text(
            recent["segments"]
        )
    )

    print("\n--- Search: microphone ---")

    search_result = search_meeting("microphone")

    print(
        segments_to_text(
            search_result["segments"]
        )
    )


if __name__ == "__main__":
    print("\n--- Saved Documents ---")
    print(list_saved_documents())

    print("\n--- Goa Travel Guide Summary ---")
    print(get_document_summary("Goa-Travel-Guide.pdf"))

    print("\n--- Search: Goa ---")
    print(search_saved_documents("Goa"))