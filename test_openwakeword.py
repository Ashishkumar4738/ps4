import time

import numpy as np
import sounddevice as sd
import openwakeword
from openwakeword.model import Model

SAMPLE_RATE = 16000
CHUNK_SIZE = 1280  # 80 ms at 16 kHz
THRESHOLD = 0.5

model_path = openwakeword.models["hey_jarvis"]["model_path"]
model = Model(wakeword_model_paths=[model_path])

print("Wake-word test started.")
print("Say: Hey Jarvis")
print("Press Ctrl+C to stop.\n")

try:
    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=CHUNK_SIZE,
        channels=1,
        dtype="int16",
    ) as stream:
        while True:
            audio_bytes, overflowed = stream.read(CHUNK_SIZE)
            audio = np.frombuffer(audio_bytes, dtype=np.int16)

            predictions = model.predict(audio)
            score = max(predictions.values(), default=0.0)

            if score >= THRESHOLD:
                print(f"[WAKE WORD DETECTED] score={score:.3f}")
                model.reset()

            time.sleep(0.001)

except KeyboardInterrupt:
    print("\nTest stopped.")
