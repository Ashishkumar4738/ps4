import subprocess

from config import WHISPER, MODEL


# ============================================================
# Whisper
# ============================================================

def transcribe(filename):

    print()
    print(f"[WHISPER START] {filename}")

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

    lines = []

    for line in result.stdout.splitlines():

        line = line.strip()

        if not line:
            continue

        # Ignore common whisper timing/log lines
        if line.startswith("whisper_"):
            continue

        lines.append(line)

    transcription = " ".join(lines).strip()

    print(f"[WHISPER DONE] {filename}")

    return transcription
