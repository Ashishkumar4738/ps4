import re
from nova_agent import ask_nova


# ============================================================
# Configuration
# ============================================================

WAKE_PHRASE = "hey nova"

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

        if not text:
            return None

        # ----------------------------------------------------
        # IDLE STATE
        # ----------------------------------------------------

        if not self.active:

            if self.contains_wake_phrase(text):

                self.active = True

                command = self.remove_wake_phrase(text)

                print("\n[Nova] Wake phrase detected.")

                # User may have said:
                #
                # "Hey Nova, summarize the meeting."
                #
                # in the same Whisper segment.

                if command:

                    print(
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

        print(
            f"[Nova] Command received: {text}"
        )

        return self.execute_command(text)

    # --------------------------------------------------------
    # Execute Nova command
    # --------------------------------------------------------

    def execute_command(self, command):

        try:

            response = ask_nova(command)

            print(
                f"\nNova: {response}\n"
            )

            return response

        except Exception as e:

            print(
                f"\n[Nova Error] {e}\n"
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