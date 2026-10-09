
import time

import numpy as np
import openwakeword
from openwakeword.model import Model

from logger_config import logger


class WakeWordDetector:
    def __init__(self, threshold=0.5, cooldown_seconds=2.0):
        model_path = openwakeword.models["hey_jarvis"]["model_path"]

        self.model = Model(
            wakeword_model_paths=[model_path]
        )

        self.threshold = threshold
        self.cooldown_seconds = cooldown_seconds
        self.last_detection_time = 0.0
        self.armed = True

        logger.info("[WAKE WORD] Hey Jarvis model loaded")

    def process_audio(self, audio_bytes):
        """Process signed 16-bit, mono, 16 kHz microphone audio."""
        audio = np.frombuffer(audio_bytes, dtype=np.int16)

        # openWakeWord works best with 80 ms audio chunks.
        # Buffer incoming audio until 1280 samples are available.
        if not hasattr(self, "_audio_buffer"):
            self._audio_buffer = np.empty(0, dtype=np.int16)

        self._audio_buffer = np.concatenate(
            (self._audio_buffer, audio)
        )

        detected = False

        while len(self._audio_buffer) >= 1280:
            chunk = self._audio_buffer[:1280]
            self._audio_buffer = self._audio_buffer[1280:]

            predictions = self.model.predict(chunk)
            score = max(predictions.values(), default=0.0)
            now = time.monotonic()

            if score < self.threshold:
                self.armed = True

            if (
                score >= self.threshold
                and self.armed
                and now - self.last_detection_time
                >= self.cooldown_seconds
            ):
                self.last_detection_time = now
                self.armed = False
                detected = True

                logger.info(
                    "[WAKE WORD] Hey Jarvis detected (score=%.3f)",
                    score,
                )

        return detected
