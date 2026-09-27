import os
import subprocess
import tempfile

import sounddevice as sd
import soundfile as sf


PIPER_MODEL = "/home/ashish/ps4/models/tts/en_US-lessac-medium.onnx"


def speak(text):
    if not text:
        return

    text = text.strip()

    if not text:
        return

    # Temporary WAV file
    with tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    ) as temp:
        wav_file = temp.name

    try:
        # Generate speech with Piper
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

        # Load generated audio
        audio, sample_rate = sf.read(wav_file)

        # Play through default PulseAudio output
        sd.play(audio, sample_rate)
        sd.wait()

    finally:
        if os.path.exists(wav_file):
            os.remove(wav_file)