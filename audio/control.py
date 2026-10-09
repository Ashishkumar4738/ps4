
import threading
from logger_config import logger

_tts_process = None
_lock = threading.Lock()
_speech_enabled = True


def is_speech_enabled():
    """Return whether Nova is allowed to speak."""
    with _lock:
        return _speech_enabled


def set_speech_enabled(enabled):
    """Enable or disable speech and interrupt playback if disabled."""
    global _speech_enabled

    with _lock:
        _speech_enabled = bool(enabled)

    if not enabled:
        stop_speaking()

    logger.info(
        "[TTS] Speech %s",
        "enabled" if enabled else "disabled"
    )
    return bool(enabled)


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
            logger.info("[TTS] Nothing is currently playing.")
            return False

        if process.poll() is not None:
            _tts_process = None
            return False

        logger.info("[TTS] Stopping playback.")
        process.terminate()
        _tts_process = None
        return True
