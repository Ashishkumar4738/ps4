import os
import subprocess
import tempfile
import time
from logger_config import logger
from audio.control import (
    set_tts_process,
    clear_tts_process,
)

PIPER_MODEL = "/home/ashish-kumar/Projects/ps4/models/tts/en_US-lessac-medium.onnx"

PAPLAY = "/usr/bin/paplay"
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
            [PAPLAY, wav_file]
        )

        set_tts_process(player)

        print("[TTS] Waiting for playback...")

        try:
            player.wait()
        finally:
            clear_tts_process(player)
            
        time.sleep(1)  # Small delay to ensure playback finishes
        print("[TTS] Playback finished")

    finally:

        if os.path.exists(wav_file):
            os.remove(wav_file)

            print("[TTS] Temporary file removed")