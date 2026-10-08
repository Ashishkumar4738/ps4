import threading

from evdev import InputDevice, ecodes

from audio.control import stop_speaking


KEYBOARD_DEVICE = "/dev/input/event2"


def _keyboard_listener():

    device = InputDevice(KEYBOARD_DEVICE)

    print(
        f"[AUDIO] Keyboard listener started: "
        f"{device.name}"
    )

    for event in device.read_loop():

        if event.type != ecodes.EV_KEY:
            continue

        # Right Ctrl pressed
        if (
            event.code == ecodes.KEY_RIGHTCTRL
            and event.value == 1
        ):
            stop_speaking()


def start_audio_control():

    thread = threading.Thread(
        target=_keyboard_listener,
        daemon=True,
        name="AudioControl"
    )

    thread.start()

    return thread