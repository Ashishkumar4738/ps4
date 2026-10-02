import re
from agent.nova_agent import ask_nova
from logger_config import logger

# ============================================================
# Configuration
# ============================================================

WAKE_PHRASE = "computer"

# Number of seconds after wake phrase during which
# we expect the command.
COMMAND_TIMEOUT = 10


# ============================================================
# Nova Listener
# ============================================================

class NovaListener:

    def __init__(self):
        self.active = False

    # --------------------------------------------------------
    # Check for wake phrase
    # --------------------------------------------------------

    def contains_wake_phrase(self, text):
        text = text.lower().strip()
        logger.debug(f"Checking for wake phrase in text: {text}")
        return WAKE_PHRASE in text

    # --------------------------------------------------------
    # Remove wake phrase from transcript
    # --------------------------------------------------------

    def remove_wake_phrase(self, text):
        pattern = re.compile(
            re.escape(WAKE_PHRASE),
            re.IGNORECASE
        )

        return pattern.sub("", text).strip()

    # --------------------------------------------------------
    # Process transcript
    # --------------------------------------------------------

    def process(self, text):

        text = text.strip()

        # Reset for every new transcription
        self.last_was_command = False

        if not text:
            return None

        # ----------------------------------------------------
        # IDLE STATE
        # ----------------------------------------------------

        if not self.active:

            if self.contains_wake_phrase(text):

                # This transcription IS a Nova command
                self.last_was_command = True

                self.active = True

                command = self.remove_wake_phrase(text)

                logger.info("\n[Nova] Wake phrase detected.")

                # User may have said:
                #
                # "Hey Noah, summarize the meeting."
                #
                # in the same Whisper segment.

                if command:

                    logger.info(
                        f"[Nova] Command: {command}"
                    )

                    return self.execute_command(command)

                print(
                    "[Nova] Listening for command..."
                )

                return None

            # Normal meeting conversation
            return None

        # ----------------------------------------------------
        # COMMAND STATE
        # ----------------------------------------------------

        # Since Nova is active, this is also a command
        self.last_was_command = True

        logger.info(
            f"[Nova] Command received: {text}"
        )

        return self.execute_command(text)
    # --------------------------------------------------------
    # Execute Nova command
    # --------------------------------------------------------

    def execute_command(self, command):

        try:

            response = ask_nova(command)

            logger.info(
                "Nova response: %s",
                response
            )

            return response

        except Exception as e:

            logger.exception(
                "Nova Error: %s",
                e
            )

            return None

        finally:

            # Return to normal listening mode
            self.active = False


# ============================================================
# Standalone test
# ============================================================

if __name__ == "__main__":

    nova = NovaListener()

    print("=" * 60)
    print("Nova Wake Phrase Test")
    print("=" * 60)

    print("\nWake phrase:", WAKE_PHRASE)
    print("Type transcript segments below.")
    print("Type 'exit' to quit.\n")

    while True:

        text = input("Transcript: ").strip()

        if text.lower() == "exit":
            break

        nova.process(text)