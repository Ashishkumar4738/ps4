import wave

from config import SAMPLE_RATE, CHANNELS

# ============================================================
# WAV handling
# ============================================================
def save_wav(filename, frames):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b"".join(frames))