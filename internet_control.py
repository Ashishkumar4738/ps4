import threading
from evdev import InputDevice, ecodes
from logger_config import logger

# ============================================================
# Internet state
# ============================================================

_internet_enabled = True
_lock = threading.Lock()


class InternetDisabledError(Exception):
    """Raised when Internet access is disabled."""
    pass


def is_internet_enabled():
    """Return the current Internet access state."""
    with _lock:
        return _internet_enabled


def require_internet():
    """
    Ensure Internet access is enabled.

    Raises:
        InternetDisabledError: If Internet access is disabled.
    """
    if not is_internet_enabled():
        logger.warning(
            "[INTERNET ACCESS BLOCKED] Internet access is disabled."
        )
        raise InternetDisabledError(
            "Internet access is currently disabled."
        )


def toggle_internet():
    """Toggle Internet access state."""
    global _internet_enabled

    with _lock:
        _internet_enabled = not _internet_enabled
        state = _internet_enabled

    print(
        f"[INTERNET] "
        f"{'ENABLED' if state else 'DISABLED'}"
    )

    return state


# ============================================================
# Keyboard listener
# ============================================================

KEYBOARD_DEVICE = "/dev/input/event2"


def _keyboard_listener():
    """Listen for Right Shift and toggle Internet access."""

    device = InputDevice(KEYBOARD_DEVICE)
    logger.info(
        f"[INTERNET] Listening for Right Shift on: "
    )
    print(
        f"[INTERNET] Keyboard listener started: "
        f"{device.name}"
    )

    for event in device.read_loop():

        if event.type != ecodes.EV_KEY:
            continue

        # event.value == 1 means key pressed
        if event.code == ecodes.KEY_RIGHTSHIFT and event.value == 1:
            toggle_internet()


def start_internet_toggle():
    """Start the Right Shift listener in the background."""
    logger.info(
        "[INTERNET] Starting Right Shift listener for Internet toggle..."
    )
    thread = threading.Thread(
        target=_keyboard_listener,
        daemon=True,
        name="InternetToggle"
    )

    thread.start()

    return thread