import threading
from logger_config import logger


# ============================================================
# Current TTS process
# ============================================================

_tts_process = None
_lock = threading.Lock()


def set_tts_process(process):
    """Register the currently playing TTS process."""

    global _tts_process

    with _lock:
        _tts_process = process


def clear_tts_process(process=None):
    """Clear the current TTS process reference."""

    global _tts_process

    with _lock:

        if process is None or _tts_process is process:
            _tts_process = None


def stop_speaking():
    """Immediately stop the currently playing TTS audio."""

    global _tts_process

    with _lock:
        process = _tts_process

        if process is None:
            logger.info("[TTS] Stop requested, but nothing is playing.")
            return False

        if process.poll() is not None:
            _tts_process = None
            return False

        logger.info("[TTS] Stop requested. Stopping playback.")

        process.terminate()

        _tts_process = None

        return True