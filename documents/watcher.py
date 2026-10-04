
import logging
import queue
import threading
import time

from pathlib import Path

from documents.parser import parse_document
from documents.summarizer import summarize_document
from documents.document_store import (
    initialize_store,
    save_summary,
    calculate_file_hash,
    load_all_documents,
)


# ============================================================
# Configuration
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent

INBOX_DIR = PROJECT_DIR / "document_inbox"

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".md",
}

POLL_INTERVAL = 2
STABLE_CHECKS = 2
RETRY_DELAY = 15

logger = logging.getLogger(__name__)

document_queue = queue.Queue()
stop_event = threading.Event()

state_lock = threading.Lock()

# path -> (file signature, stable count)
file_states = {}

# Paths currently waiting in the queue or being processed.
queued_paths = set()

# path -> (last failed signature, retry after timestamp)
retry_states = {}


# ============================================================
# Logging
# ============================================================

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
    )


# ============================================================
# File helpers
# ============================================================

def get_signature(path):
    """
    Return a signature that changes when a file changes.
    """

    stat = path.stat()

    return (
        stat.st_size,
        stat.st_mtime_ns,
    )


def is_supported_document(path):
    return (
        path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
        and not path.name.startswith("~$")
    )


def already_processed(path, file_hash):
    """
    Skip a file when the same source path and content
    already have a successfully saved summary.
    """

    source_path = str(path.resolve())

    for record in load_all_documents():
        if (
            record.get("source_path") == source_path
            and record.get("file_hash") == file_hash
            and record.get("status") == "processed"
            and record.get("summary")
        ):
            return True

    return False


# ============================================================
# Document processing
# ============================================================

def process_document(filename):
    """
    Parse, summarize, and persist a document.
    """

    path = Path(filename).resolve()

    logger.info("Processing document: %s", path.name)

    # Hashing also verifies that the file is readable.
    file_hash = calculate_file_hash(path)

    if already_processed(path, file_hash):
        logger.info(
            "Unchanged document already processed: %s",
            path.name,
        )
        return

    document = parse_document(str(path))

    result = summarize_document(document)

    record = save_summary(
        filename=str(path),
        summary=result["summary"],
        file_hash=file_hash,
        chunk_count=result.get("chunk_count", 0),
    )

    logger.info(
        "Summary saved: %s (ID: %s)",
        path.name,
        record["document_id"],
    )


# ============================================================
# Background worker
# ============================================================

def document_worker():
    """
    Process queued documents without blocking the watcher.
    """

    logger.info("Document worker started")

    while True:
        try:
            filename = document_queue.get(timeout=0.5)

        except queue.Empty:
            if stop_event.is_set():
                break
            continue

        path = Path(filename)

        try:
            if not stop_event.is_set():
                process_document(path)

                # A previous failure should not delay future
                # processing after a successful run.
                with state_lock:
                    retry_states.pop(str(path), None)

        except Exception:
            logger.exception(
                "Document processing failed: %s",
                path.name,
            )

            # Retry after a delay, without blocking other files.
            try:
                signature = get_signature(path)

                with state_lock:
                    retry_states[str(path)] = (
                        signature,
                        time.monotonic() + RETRY_DELAY,
                    )

            except OSError:
                logger.warning(
                    "File is no longer accessible: %s",
                    path,
                )

        finally:
            with state_lock:
                queued_paths.discard(str(path))

            document_queue.task_done()

    logger.info("Document worker stopped")


# ============================================================
# Folder watcher
# ============================================================

def watch_folder():
    """
    Watch the inbox and queue stable documents.

    Existing documents are also discovered on startup.
    Press Ctrl+C to stop the watcher.
    """

    INBOX_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    initialize_store()
    setup_logging()

    stop_event.clear()

    worker = threading.Thread(
        target=document_worker,
        name="document-worker",
        daemon=True,
    )

    worker.start()

    logger.info("Watching folder: %s", INBOX_DIR)
    logger.info("Supported formats: PDF, DOCX, TXT, MD")

    try:
        while not stop_event.is_set():

            try:
                paths = list(INBOX_DIR.iterdir())
            except OSError:
                logger.exception("Could not scan inbox")
                stop_event.wait(POLL_INTERVAL)
                continue

            for path in paths:
                if not is_supported_document(path):
                    continue

                key = str(path.resolve())

                try:
                    signature = get_signature(path)
                except OSError:
                    continue

                with state_lock:
                    previous = file_states.get(key)

                    if previous and previous[0] == signature:
                        stable_count = previous[1] + 1
                    else:
                        stable_count = 0

                    file_states[key] = (
                        signature,
                        stable_count,
                    )

                    if stable_count < STABLE_CHECKS:
                        continue

                    if key in queued_paths:
                        continue

                    retry = retry_states.get(key)

                    if retry:
                        retry_signature, retry_after = retry

                        if retry_signature != signature:
                            retry_states.pop(key, None)

                        elif time.monotonic() < retry_after:
                            continue

                        else:
                            retry_states.pop(key, None)

                    queued_paths.add(key)

                document_queue.put(str(path.resolve()))

            stop_event.wait(POLL_INTERVAL)

    except KeyboardInterrupt:
        logger.info("Stop requested")

    finally:
        stop_event.set()

        # Finish work already waiting in the queue.
        document_queue.join()
        worker.join()

        logger.info("Document watcher stopped")


if __name__ == "__main__":
    watch_folder()