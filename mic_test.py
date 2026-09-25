import os
import wave
import time
import json
import queue
import subprocess
from datetime import datetime

import sounddevice as sd
import webrtcvad


# ============================================================
# Configuration
# ============================================================

SAMPLE_RATE = 16000
CHANNELS = 1

FRAME_MS = 30
FRAME_SAMPLES = SAMPLE_RATE * FRAME_MS // 1000

VAD_MODE = 2

# Stop recording after this much silence
SILENCE_DURATION_MS = 700

# Ignore extremely short sounds
MIN_SPEECH_MS = 300

# Maximum length of one speech segment
MAX_SEGMENT_SECONDS = 30

AUDIO_DIR = "/tmp/ps4_audio"

MEETING_DIR = os.path.expanduser("~/ps4/meetings")
MEETING_FILE = os.path.join(MEETING_DIR, "meeting.json")

WHISPER = os.path.expanduser(
    "~/ps4/whisper.cpp/build/bin/whisper-cli"
)

MODEL = os.path.expanduser(
    "~/ps4/whisper.cpp/models/ggml-small.en.bin"
)


# ============================================================
# Setup
# ============================================================

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(MEETING_DIR, exist_ok=True)

vad = webrtcvad.Vad(VAD_MODE)


# ============================================================
# Meeting file
# ============================================================

meeting_start = datetime.now()

meeting_data = {
    "meeting_id": meeting_start.strftime("%Y%m%d_%H%M%S"),
    "started_at": meeting_start.isoformat(),
    "segments": []
}


def save_meeting():
    """
    Save the complete meeting transcription.
    """
    with open(MEETING_FILE, "w", encoding="utf-8") as f:
        json.dump(
            meeting_data,
            f,
            indent=2,
            ensure_ascii=False
        )


save_meeting()


# ============================================================
# WAV handling
# ============================================================

def save_wav(filename, frames):

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # int16
        wf.setframerate(SAMPLE_RATE)

        wf.writeframes(b"".join(frames))


# ============================================================
# Whisper
# ============================================================

def transcribe(filename):

    print("\n[PROCESSING]")

    cmd = [
        WHISPER,

        "-m",
        MODEL,

        "-f",
        filename,

        "-l",
        "en",

        "-nt",
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        print("[WHISPER ERROR]")
        print(result.stderr)

        return ""

    # whisper-cli may print additional information.
    # Remove empty lines and keep the transcription.
    lines = []

    for line in result.stdout.splitlines():

        line = line.strip()

        if not line:
            continue

        # Ignore common whisper timing/log lines
        if line.startswith("whisper_"):
            continue

        lines.append(line)

    return " ".join(lines).strip()


# ============================================================
# Main loop
# ============================================================

print("==============================================")
print(" PS4 Meeting Transcription")
print("==============================================")

print(f"Meeting file:")
print(f"  {MEETING_FILE}")

print()

print("Speak normally.")
print("Press Ctrl+C to stop.")
print()


segment_id = 0


try:

    while True:

        print("[LISTENING]")

        audio_queue = queue.Queue()

        frames = []

        speech_started = False

        silence_frames = 0
        speech_frames = 0

        segment_start = None

        def callback(
            indata,
            frames_count,
            time_info,
            status
        ):

            if status:

                print("[AUDIO]", status)

            audio_queue.put(bytes(indata))


        # ----------------------------------------------------
        # Capture one speech segment
        # ----------------------------------------------------

        with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=FRAME_SAMPLES,
            channels=CHANNELS,
            dtype="int16",
            callback=callback
        ):

            while True:

                frame = audio_queue.get()

                is_speech = vad.is_speech(
                    frame,
                    SAMPLE_RATE
                )

                if is_speech:

                    if not speech_started:

                        print("[START SPEAKING]")

                        speech_started = True

                        segment_start = time.time()

                    frames.append(frame)

                    speech_frames += 1

                    silence_frames = 0

                elif speech_started:

                    frames.append(frame)

                    silence_frames += 1

                    silence_duration = (
                        silence_frames * FRAME_MS
                    )

                    # User stopped speaking
                    if silence_duration >= SILENCE_DURATION_MS:

                        break

                # ------------------------------------------------
                # Safety limit
                # ------------------------------------------------

                if speech_started:

                    duration = time.time() - segment_start

                    if duration >= MAX_SEGMENT_SECONDS:

                        print("[MAX SEGMENT LENGTH]")

                        break


        # ----------------------------------------------------
        # Validate speech
        # ----------------------------------------------------

        speech_duration_ms = speech_frames * FRAME_MS

        if speech_duration_ms < MIN_SPEECH_MS:

            print("[IGNORED: TOO SHORT]")

            continue


        # ----------------------------------------------------
        # Create temporary WAV
        # ----------------------------------------------------

        segment_id += 1

        filename = os.path.join(
            AUDIO_DIR,
            f"chunk_{segment_id:04d}.wav"
        )

        save_wav(
            filename,
            frames
        )

        duration_seconds = (
            len(frames) * FRAME_MS / 1000
        )

        print(
            f"[AUDIO SAVED] {filename}"
        )

        print(
            f"[DURATION] {duration_seconds:.2f}s"
        )


        # ----------------------------------------------------
        # Transcribe
        # ----------------------------------------------------

        transcription = transcribe(filename)


        if transcription:

            print()
            print("[TRANSCRIPTION]")
            print(transcription)


            # --------------------------------------------
            # Add to meeting JSON
            # --------------------------------------------

            segment = {

                "segment_id": segment_id,

                "timestamp": datetime.now().isoformat(),

                "duration_seconds": round(
                    duration_seconds,
                    2
                ),

                "text": transcription
            }


            meeting_data["segments"].append(
                segment
            )


            # Save immediately
            save_meeting()

            print()
            print(
                f"[SAVED TO MEETING] "
                f"{MEETING_FILE}"
            )

        else:

            print(
                "[NO TRANSCRIPTION]"
            )


        # ----------------------------------------------------
        # Delete temporary audio
        # ----------------------------------------------------

        if os.path.exists(filename):

            os.remove(filename)

            print(
                "[DELETED TEMP AUDIO]"
            )


        print()


except KeyboardInterrupt:

    meeting_data["ended_at"] = datetime.now().isoformat()

    save_meeting()

    print()
    print("==============================================")
    print(" Meeting stopped")
    print("==============================================")

    print()
    print(
        f"Transcript saved to:"
    )

    print(
        f"  {MEETING_FILE}"
    )

    print()

    print(
        f"Total segments: "
        f"{len(meeting_data['segments'])}"
    )