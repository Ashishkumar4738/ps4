import json
from datetime import datetime, timedelta
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

MEETING_FILE = Path(__file__).resolve().parent.parent /"meetings" / "meeting.json"


# ============================================================
# Internal helpers
# ============================================================

def load_meeting():
    """Load the current meeting.json file."""
    if not MEETING_FILE.exists():
        raise FileNotFoundError(
            f"Meeting file not found: {MEETING_FILE}"
        )

    with open(MEETING_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


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

def get_recent_transcript(minutes):
    """
    Get transcript from the most recent `minutes`.

    Example:

        get_recent_transcript(10)
    """

    meeting = load_meeting()

    if minutes <= 0:
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
# Simple local test
# ============================================================

if __name__ == "__main__":

    print("\n=== Nova Tools Test ===\n")

    meeting = load_meeting()

    print("Meeting ID:")
    print(meeting.get("meeting_id"))

    print("\nTotal segments:")
    print(len(meeting.get("segments", [])))

    print("\n--- Recent transcript (5 minutes) ---")

    recent = get_recent_transcript(5)

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