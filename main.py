import queue

from audio.recorder import AudioRecorder
from transcription.worker import TranscriptionWorker
from meeting.manager import MeetingManager
from logger_config import logger
from internet_control import start_internet_toggle
from audio.keyboard import start_audio_control
# ============================================================
# Main
# ============================================================

def main():

    logger.info("==============================================")
    logger.info(" PS4 Meeting Transcription")
    logger.info("==============================================")
    start_internet_toggle()
    start_audio_control()
    # --------------------------------------------------------
    # Meeting
    # --------------------------------------------------------

    meeting = MeetingManager()

    logger.info("Meeting file:")
    logger.info(f"  {meeting.file_path}")

    # --------------------------------------------------------
    # Transcription queue
    # --------------------------------------------------------

    transcription_queue = queue.Queue()

    # --------------------------------------------------------
    # Audio recorder
    # --------------------------------------------------------

    recorder = AudioRecorder(
        on_segment=transcription_queue.put
    )

    # --------------------------------------------------------
    # Transcription worker
    # --------------------------------------------------------

    worker = TranscriptionWorker(
        transcription_queue=transcription_queue,
        meeting=meeting,
        recorder=recorder
    )

    # --------------------------------------------------------
    # Start worker
    # --------------------------------------------------------

    worker.start()

    print()
    print("Speak normally.")
    print("Press Ctrl+C to stop.")
    print()

    # --------------------------------------------------------
    # Start microphone
    # --------------------------------------------------------

    try:

        recorder.run()

    except KeyboardInterrupt:

        print()
        print("[STOPPING MEETING]")

    finally:

        # ----------------------------------------------------
        # Stop microphone
        # ----------------------------------------------------

        recorder.stop()

        # ----------------------------------------------------
        # Wait for transcription queue
        # ----------------------------------------------------

        print()
        print("[WAITING FOR TRANSCRIPTION QUEUE]")

        worker.wait_until_finished()

        # ----------------------------------------------------
        # Stop transcription worker
        # ----------------------------------------------------

        worker.stop()

        # ----------------------------------------------------
        # Finish meeting
        # ----------------------------------------------------

        meeting.finish()

        # ----------------------------------------------------
        # Final information
        # ----------------------------------------------------

        print()
        print("==============================================")
        print(" Meeting stopped")
        print("==============================================")

        print()

        print("Transcript saved to:")
        print(f"  {meeting.file_path}")

        print()

        print(
            f"Total segments: "
            f"{meeting.get_segment_count()}"
        )

        print()

        print("All transcription completed.")


if __name__ == "__main__":
    main()