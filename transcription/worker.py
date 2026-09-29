import os
import time
import queue
import threading

from transcription.whisper import transcribe
from tts import speak
from agent.nova_listener import NovaListener


class TranscriptionWorker:

    def __init__(
        self,
        transcription_queue,
        meeting,
        recorder
    ):
        self.transcription_queue = transcription_queue
        self.meeting = meeting

        self.recorder = recorder

        self.stop_event = threading.Event()

        self.nova = NovaListener()

        self.thread = threading.Thread(
            target=self.run,
            daemon=True
        )

    def start(self):
        self.thread.start()

    def run(self):
        print("[TRANSCRIPTION WORKER] Started")

        while True:

            try:
                item = self.transcription_queue.get(
                    timeout=0.5
                )

            except queue.Empty:

                if self.stop_event.is_set():
                    break

                continue

            # None means shutdown
            if item is None:
                self.transcription_queue.task_done()
                break

            segment_id = item["segment_id"]
            filename = item["filename"]
            duration_seconds = item["duration_seconds"]
            timestamp = item["timestamp"]

            try:

                # --------------------------------------------
                # Transcribe
                # --------------------------------------------

                transcription = transcribe(filename)

                if transcription:

                    print()
                    print("==============================================")
                    print(f"[TRANSCRIPTION #{segment_id}]")
                    print(transcription)
                    print("==============================================")

                    # ----------------------------------------
                    # Send transcript to Nova
                    # ----------------------------------------

                    nova_response = self.nova.process(
                        transcription
                    )

                    # ----------------------------------------
                    # Save normal meeting conversation
                    # ----------------------------------------

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

                        self.meeting.add_segment(segment)

                        print(
                            f"[SAVED TO MEETING] "
                            f"{self.meeting.file_path}"
                        )

                    else:

                        print()
                        print("==============================================")
                        print("[NOVA COMMAND DETECTED]")
                        print("[MICROPHONE] DISABLED")
                        print("==============================================")

                        # Disable microphone immediately
                        self.recorder.disable()

                        print(
                            "[NOVA COMMAND] "
                            "Not saved to meeting.json"
                        )

                    # ----------------------------------------
                    # Speak Nova response
                    # ----------------------------------------

                    if nova_response:

                        print()
                        print("==============================================")
                        print("[NOVA RESPONSE]")
                        print(nova_response)
                        print("==============================================")

                        try:

                            print("[NOVA TTS] Speaking...")

                            # Microphone is already disabled
                            speak(nova_response)

                            print("[NOVA TTS] Done")

                            # Give the microphone/audio
                            # system a moment to settle
                            time.sleep(0.2)

                        except Exception as e:

                            print(
                                f"[NOVA TTS ERROR] {e}"
                            )

                        finally:

                            # ALWAYS re-enable microphone
                            # after command
                            if self.nova.last_was_command:

                                print(
                                    "[NOVA COMMAND] "
                                    "Re-enabling microphone..."
                                )

                                # Remove audio frames that
                                # arrived while disabled
                                self.recorder.clear_audio_queue()
                                self.recorder.enable()

            except Exception as e:

                print(
                    f"[TRANSCRIPTION WORKER ERROR] "
                    f"Segment {segment_id}: {e}"
                )

            finally:

                # Delete temporary WAV
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

        print("[TRANSCRIPTION WORKER] Stopped")

    def wait_until_finished(self):
        self.transcription_queue.join()

    def stop(self):
        self.stop_event.set()

        self.transcription_queue.put(None)

        self.thread.join()