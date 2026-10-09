import os
from pathlib import Path
SAMPLE_RATE = 16000
CHANNELS = 1
FRAME_MS = 30
FRAME_SAMPLES = SAMPLE_RATE * FRAME_MS // 1000

VAD_MODE = 2
SILENCE_DURATION_MS = 700
MIN_SPEECH_MS = 300
MAX_SEGMENT_SECONDS = 20

AUDIO_DIR = "/tmp/ps4_audio"
WAKE_PHRASE = "computer"
MEETING_DIR = os.path.expanduser("~/ps4/meetings")
MEETING_FILE = os.path.join(MEETING_DIR, "meeting.json")

WHISPER = os.path.expanduser(
    "/home/ashish-kumar/Projects/ps4/whisper.cpp/build/bin/whisper-cli"
)

MODEL = os.path.expanduser(
    "/home/ashish-kumar/Projects/ps4/whisper.cpp/models/ggml-small.en.bin"
)

MODEL_NAME = "llama3.2:3b"
# MODEL_NAME = "qwen3:4b"
# MODEL_NAME = "llama3.1:8b"

SYSTEM_PROMPT_FILE = (
    Path(__file__).resolve().parent /".."/ "agent" / "system_prompt.txt"
)

# ============================================================
# Database
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_DIR / "data"
DATABASE_FILE = DATA_DIR / "nova.db"