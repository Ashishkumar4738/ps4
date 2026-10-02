import os
import queue
import threading
import time

from transcription.whisper import transcribe
from tts import speak
from agent.nova_listener import NovaListener


class TranscriptionWorker:

    def __init__(
        self,
        transcription_queue,
        meeting,
        recorder,
        worker_count=2
    ):
        self.transcription_queue = transcription_queue
        self.meeting = meeting
        self.recorder = recorder

        self.worker_count = worker_count

        self.stop_event = threading.Event()

        # ----------------------------------------------------
        # Whisper workers
        # ----------------------------------------------------

        self.workers = []

        self.stop_event = threading.Event()

        self.nova = NovaListener()
        
        self.workers = []

        # ----------------------------------------------------
        # Transcription results
        # ----------------------------------------------------

        self.result_queue = queue.Queue()

        # ----------------------------------------------------
        # Result processor
        #
        # Only ONE thread handles:
        #   - Nova
        #   - meeting.json
        #   - TTS
        #   - microphone control
        # ----------------------------------------------------

        self.processor_thread = threading.Thread(
            target=self.process_results,
            daemon=True
        )

        # ----------------------------------------------------
        # Result ordering
        # ----------------------------------------------------

        self.pending_results = {}
        self.next_segment_id = 1

    # ========================================================
    # START
    # ========================================================

    def start(self):

        print(
            f"[TRANSCRIPTION] Starting "
            f"{self.worker_count} Whisper workers"
        )

        # Start Whisper workers

        for worker_id in range(self.worker_count):

            thread = threading.Thread(
                target=self.transcription_worker,
                args=(worker_id,),
                daemon=True
            )

            thread.start()

            self.workers.append(thread)

        # Start result processor

        self.processor_thread.start()

    # ========================================================
    # WHISPER WORKER
    # ========================================================

    def transcription_worker(self, worker_id):

        print(
            f"[WHISPER WORKER {worker_id}] Started"
        )

        while True:

            try:

                item = self.transcription_queue.get(
                    timeout=0.5
                )

            except queue.Empty:

                if self.stop_event.is_set():
                    break

                continue

            # ------------------------------------------------
            # Shutdown
            # ------------------------------------------------

            if item is None:

                self.transcription_queue.task_done()

                break

            segment_id = item["segment_id"]
            filename = item["filename"]
            duration_seconds = item["duration_seconds"]
            timestamp = item["timestamp"]

            try:

                print(
                    f"[WHISPER {worker_id}] "
                    f"Transcribing segment {segment_id}"
                )

                # --------------------------------------------
                # Whisper
                # --------------------------------------------

                transcription = transcribe(filename)

                print(
                    f"[WHISPER {worker_id}] "
                    f"Finished segment {segment_id}"
                )

                # --------------------------------------------
                # Send result to processor
                # --------------------------------------------

                self.result_queue.put({
                    "segment_id": segment_id,
                    "filename": filename,
                    "duration_seconds": duration_seconds,
                    "timestamp": timestamp,
                    "transcription": transcription
                })

            except Exception as e:

                print(
                    f"[WHISPER WORKER {worker_id} ERROR] "
                    f"Segment {segment_id}: {e}"
                )

                # Still send a result so the ordering system
                # doesn't wait forever for this segment.

                self.result_queue.put({
                    "segment_id": segment_id,
                    "filename": filename,
                    "duration_seconds": duration_seconds,
                    "timestamp": timestamp,
                    "transcription": "",
                    "error": str(e)
                })

            finally:

                # --------------------------------------------
                # Delete temporary WAV
                # --------------------------------------------

                if os.path.exists(filename):

                    try:

                        os.remove(filename)

                        print(
                            f"[DELETED TEMP AUDIO] "
                            f"{filename}"
                        )

                    except Exception as e:

                        print(
                            f"[DELETE ERROR] {e}"
                        )

                self.transcription_queue.task_done()

        print(
            f"[WHISPER WORKER {worker_id}] Stopped"
        )

    # ========================================================
    # RESULT PROCESSOR
    # ========================================================

    def process_results(self):

        print("[RESULT PROCESSOR] Started")

        while True:

            try:

                result = self.result_queue.get(
                    timeout=0.5
                )

            except queue.Empty:

                if (
                    self.stop_event.is_set()
                    and self.result_queue.empty()
                ):
                    break

                continue

            segment_id = result["segment_id"]

            # ------------------------------------------------
            # Store result temporarily
            #
            # This allows us to receive:
            #
            #   segment 2
            #   segment 1
            #
            # and still process:
            #
            #   segment 1
            #   segment 2
            # ------------------------------------------------

            self.pending_results[segment_id] = result

            # ------------------------------------------------
            # Process everything that is now in order
            # ------------------------------------------------

            while (
                self.next_segment_id
                in self.pending_results
            ):

                ordered_result = (
                    self.pending_results.pop(
                        self.next_segment_id
                    )
                )

                self.handle_result(
                    ordered_result
                )

                self.next_segment_id += 1

            self.result_queue.task_done()

        print("[RESULT PROCESSOR] Stopped")

    # ========================================================
    # HANDLE ONE ORDERED RESULT
    # ========================================================

    def handle_result(self, result):

        segment_id = result["segment_id"]
        transcription = result["transcription"]
        timestamp = result["timestamp"]
        duration_seconds = result["duration_seconds"]

        print()

        print(
            "=============================================="
        )

        print(
            f"[TRANSCRIPTION #{segment_id}]"
        )

        print(transcription)

        print(
            "=============================================="
        )

        # ----------------------------------------------------
        # Empty transcription
        # ----------------------------------------------------

        if not transcription:

            print(
                f"[EMPTY TRANSCRIPTION] "
                f"Segment {segment_id}"
            )

            return

        # ----------------------------------------------------
        # Send transcript to Nova
        # ----------------------------------------------------

        nova_response = self.nova.process(
            transcription
        )

        # ----------------------------------------------------
        # Normal meeting conversation
        # ----------------------------------------------------

        if not self.nova.last_was_command:

            segment = {
                "segment_id": segment_id,
                "timestamp": timestamp,
                "duration_seconds": round(
                    duration_seconds,
                    2
                ),
                "text": transcription
            }

            self.meeting.add_segment(
                segment
            )

            print(
                f"[SAVED TO MEETING] "
                f"{self.meeting.file_path}"
            )

        # ----------------------------------------------------
        # Nova command
        # ----------------------------------------------------

        else:

            print()

            print(
                "=============================================="
            )

            print("[NOVA COMMAND DETECTED]")

            print("[MICROPHONE] DISABLED")

            print(
                "=============================================="
            )

            # Disable microphone immediately

            self.recorder.disable()

            print(
                "[NOVA COMMAND] "
                "Not saved to meeting.json"
            )

        # ----------------------------------------------------
        # Speak Nova response
        # ----------------------------------------------------

        if nova_response:

            print()

            print(
                "=============================================="
            )

            print("[NOVA RESPONSE]")

            print(nova_response)

            print(
                "=============================================="
            )

            try:

                print(
                    "[NOVA TTS] Speaking..."
                )

                speak(
                    nova_response
                )

                print(
                    "[NOVA TTS] Done"
                )

                time.sleep(0.2)

            except Exception as e:

                print(
                    f"[NOVA TTS ERROR] {e}"
                )

            finally:

                if self.nova.last_was_command:

                    print(
                        "[NOVA COMMAND] "
                        "Re-enabling microphone..."
                    )

                    self.recorder.clear_audio_queue()

                    self.recorder.enable()

    # ========================================================
    # WAIT
    # ========================================================

    def wait_until_finished(self):

        self.transcription_queue.join()

        self.result_queue.join()

    # ========================================================
    # STOP
    # ========================================================

    def stop(self):

        print(
            "[TRANSCRIPTION] Stopping..."
        )

        self.stop_event.set()

        # Tell every Whisper worker to stop

        for _ in range(self.worker_count):

            self.transcription_queue.put(None)

        # Wait for Whisper workers

        for worker in self.workers:

            worker.join()

        # Wait for result processor

        self.processor_thread.join()

        print(
            "[TRANSCRIPTION] Stopped"
        )