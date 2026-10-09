
import queue
import threading

from PySide6.QtCore import QObject, Signal


class PipelineSession(QObject):
    log_message = Signal(str)
    transcription_received = Signal(str)
    response_received = Signal(str)
    status_changed = Signal(str)
    finished = Signal(bool, str)

    def __init__(self):
        super().__init__()

        self.meeting = None
        self.recorder = None
        self.worker = None
        self.recorder_thread = None
        self.shutdown_thread = None

        self._lock = threading.Lock()
        self._started = False
        self._stopping = False

    def start(self):
        with self._lock:
            if self._started:
                return False
            self._started = True

        try:
            from meeting.manager import MeetingManager
            from audio.recorder import AudioRecorder
            from transcription.worker import TranscriptionWorker

            self.meeting = MeetingManager()
            transcription_queue = queue.Queue()

            self.recorder = AudioRecorder(
                on_segment=transcription_queue.put
            )

            self.worker = TranscriptionWorker(
                transcription_queue=transcription_queue,
                meeting=self.meeting,
                recorder=self.recorder,
                on_transcription=self.transcription_received.emit,
                on_response=self.response_received.emit,
            )

            self.worker.start()

            self.recorder_thread = threading.Thread(
                target=self.recorder.run,
                name="NovaAudioRecorder",
                daemon=True,
            )
            self.recorder_thread.start()

            self.log_message.emit("[SYSTEM] Recording pipeline started.")
            self.status_changed.emit("Listening")
            return True

        except Exception as exc:
            self.log_message.emit(
                f"[ERROR] Could not start pipeline: {exc}"
            )
            self.status_changed.emit("Error")
            self.finished.emit(False, str(exc))
            return False

    def stop(self, wait=False):
        with self._lock:
            if not self._started:
                return

            if self._stopping:
                shutdown_thread = self.shutdown_thread
                already_stopping = True
            else:
                self._stopping = True
                shutdown_thread = None
                already_stopping = False

        if already_stopping:
            if wait and shutdown_thread is not None:
                shutdown_thread.join()
            return

        self.status_changed.emit("Stopping")
        self.log_message.emit("[SYSTEM] Stopping recording pipeline...")

        if self.recorder is not None:
            self.recorder.stop()

        if wait:
            self._shutdown()
        else:
            self.shutdown_thread = threading.Thread(
                target=self._shutdown,
                name="NovaPipelineShutdown",
                daemon=True,
            )
            self.shutdown_thread.start()

    def _shutdown(self):
        success = True
        message = "Session stopped."

        try:
            if self.recorder_thread is not None:
                self.recorder_thread.join()

            if self.worker is not None:
                self.worker.wait_until_finished()
                self.worker.stop()

            if self.meeting is not None:
                self.meeting.finish()

            self.log_message.emit("[SYSTEM] Meeting session saved.")

        except Exception as exc:
            success = False
            message = str(exc)
            self.log_message.emit(
                f"[ERROR] Pipeline shutdown failed: {exc}"
            )

        finally:
            with self._lock:
                self._started = False
                self._stopping = False

            self.status_changed.emit(
                "Stopped" if success else "Error"
            )
            self.finished.emit(success, message)
