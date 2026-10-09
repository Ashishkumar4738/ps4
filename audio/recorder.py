import os
import queue
import time
import threading
from agent.wake_word import WakeWordDetector

import sounddevice as sd
import webrtcvad
from logger_config import logger
from config.config import (
    SAMPLE_RATE,
    CHANNELS,
    FRAME_MS,
    FRAME_SAMPLES,
    VAD_MODE,
    SILENCE_DURATION_MS,
    MIN_SPEECH_MS,
    MAX_SEGMENT_SECONDS,
    AUDIO_DIR,
)

from audio.wav import save_wav


class AudioRecorder:

    def __init__(self, on_segment):

        self.on_segment = on_segment

        # VAD
        self.vad = webrtcvad.Vad(VAD_MODE)

        # Controls microphone
        self.mic_enabled = threading.Event()
        self.mic_enabled.set()

        # Tells active VAD loop to stop immediately
        self.mic_stop_requested = threading.Event()

        # Audio queue
        self.audio_queue = queue.Queue()

        # Segment counter
        self.segment_id = 0
        # Wake-word detector
        self.wake_word_detector = WakeWordDetector()
        self.wake_word_detected = threading.Event()

        # Make sure audio directory exists
        os.makedirs(AUDIO_DIR, exist_ok=True)

    # ========================================================
    # Microphone control
    # ========================================================

    def enable(self):

        self.mic_enabled.set()

        logger.info("[MICROPHONE] ENABLED")
        logger.info("[LISTENING]")

    def disable(self):

        logger.info("[MICROPHONE] DISABLED")

        self.mic_enabled.clear()
        self.mic_stop_requested.set()

        # Wake up audio_queue.get()
        self.audio_queue.put(None)

    def clear_audio_queue(self):

        while True:

            try:
                self.audio_queue.get_nowait()
                self.audio_queue.task_done()

            except queue.Empty:
                break

    # ========================================================
    # Audio callback
    # ========================================================

    
    def callback(
        self,
        indata,
        frames_count,
        time_info,
        status
    ):
        if status:
            logger.info("[AUDIO] %s", status)

        if not self.mic_enabled.is_set():
            self.mic_stop_requested.set()
            self.audio_queue.put(None)
            return

        audio_bytes = bytes(indata)

        # Check for the wake phrase using the same microphone stream.
        try:
            if self.wake_word_detector.process_audio(audio_bytes):
                self.wake_word_detected.set()
                print("[WAKE WORD DETECTED] Hey Jarvis")
        except Exception:
            logger.exception("[WAKE WORD] Detection failed")

        # Preserve the existing VAD and transcription pipeline.
        self.audio_queue.put(audio_bytes)

    # ========================================================
    # Capture one speech segment
    # ========================================================

    def record_segment(self):

        self.mic_stop_requested.clear()

        frames = []

        speech_started = False
        silence_frames = 0
        speech_frames = 0

        segment_start = None

        with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=FRAME_SAMPLES,
            channels=CHANNELS,
            dtype="int16",
            callback=self.callback
        ):

            while True:

                frame = self.audio_queue.get()

                # Nova requested microphone shutdown
                if (
                    frame is None
                    or self.mic_stop_requested.is_set()
                ):

                    logger.info("[MICROPHONE] Stop requested")

                    break

                is_speech = self.vad.is_speech(
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
                    if (
                        silence_duration
                        >= SILENCE_DURATION_MS
                    ):

                        break

                # ====================================================
                # Safety limit
                # ====================================================

                if speech_started:

                    duration = (
                        time.time() - segment_start
                    )

                    if duration >= MAX_SEGMENT_SECONDS:

                        print("[MAX SEGMENT LENGTH]")

                        break

        return frames, speech_frames

    # ========================================================
    # Process recorded segment
    # ========================================================

    def process_segment(
        self,
        frames,
        speech_frames,
        wake_word_detected=False,
    ):

        speech_duration_ms = (
            speech_frames * FRAME_MS
        )

        # Ignore extremely short sounds
        if speech_duration_ms < MIN_SPEECH_MS:
            print("[IGNORED: TOO SHORT]")
            return False

        # ====================================================
        # Create temporary WAV
        # ====================================================

        self.segment_id += 1

        filename = os.path.join(
            AUDIO_DIR,
            f"chunk_{self.segment_id:04d}.wav"
        )

        save_wav(
            filename,
            frames
        )

        duration_seconds = (
            len(frames) * FRAME_MS / 1000
        )

        from datetime import datetime

        timestamp = datetime.now().isoformat()

        print(
            f"[AUDIO SAVED] {filename}"
        )

        print(
            f"[DURATION] {duration_seconds:.2f}s"
        )

        # ====================================================
        # Send to transcription worker
        # ====================================================

        self.on_segment({
            "segment_id": self.segment_id,
            "filename": filename,
            "duration_seconds": duration_seconds,
            "timestamp": timestamp,
            "wake_word_detected": wake_word_detected,
        })

        print(
            f"[QUEUED FOR TRANSCRIPTION] "
            f"Segment {self.segment_id}"
        )
        return True

    # ========================================================
    # Main recorder loop
    # ========================================================

    def run(self):

        logger.info("[AUDIO RECORDER] Started")

        while True:

            # Wait until microphone is enabled
            self.mic_enabled.wait()

            # Reset stop request
            self.mic_stop_requested.clear()

            logger.info("[LISTENING]")

            frames, speech_frames = (
                self.record_segment()
            )

            # If microphone was disabled by Nova,
            # don't process the interrupted audio.
            if not self.mic_enabled.is_set():

                self.clear_audio_queue()

                continue

            wake_detected = self.wake_word_detected.is_set()
            
            queued = self.process_segment(
                frames,
                speech_frames,
                wake_word_detected=wake_detected,
            )
            
            # Clear the event only after its detection has been
            # attached to a successfully queued segment.
            if queued and wake_detected:
                self.wake_word_detected.clear()

            print("[LISTENING CONTINUES]")

    # ========================================================
    # Stop recorder
    # ========================================================

    def stop(self):

        self.mic_enabled.clear()
        self.mic_stop_requested.set()

        # Wake up queue
        self.audio_queue.put(None)

        print("[AUDIO RECORDER] Stopped")