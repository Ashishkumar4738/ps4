import os
import subprocess
import tempfile
import time
from logger_config import logger

PIPER_MODEL = "/home/ashish/ps4/models/tts/en_US-lessac-medium.onnx"


def speak(text):

    if not text:
        return

    text = text.strip()

    if not text:
        return

    with tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    ) as temp:
        wav_file = temp.name

    try:

        logger.info("[TTS] Generating Piper audio...")

        subprocess.run(
            [
                "piper",
                "-m",
                PIPER_MODEL,
                "-f",
                wav_file,
            ],
            input=text.encode("utf-8"),
            check=True,
        )

        print("[TTS] Piper generation complete")

        print("[TTS] Starting playback...")

        player = subprocess.Popen(
            ["paplay", wav_file]
        )

        print("[TTS] Waiting for playback...")

        player.wait()
        time.sleep(2)  # Small delay to ensure playback finishes
        print("[TTS] Playback finished")

    finally:

        if os.path.exists(wav_file):
            os.remove(wav_file)

            print("[TTS] Temporary file removed")