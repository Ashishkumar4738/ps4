
import re
import time

from agent.nova_agent import ask_nova
from logger_config import logger

WAKE_PHRASE = "hey jarvis"
COMMAND_TIMEOUT = 10


class NovaListener:
    def __init__(self):
        self.active = False
        self.last_was_command = False
        self.activation_time = 0.0

    def contains_wake_phrase(self, text):
        return WAKE_PHRASE in text.lower().strip()

    def remove_wake_phrase(self, text):
        pattern = re.compile(re.escape(WAKE_PHRASE), re.IGNORECASE)
        return pattern.sub("", text).strip(" ,.!?")

    def activate_from_wake_word(self):
        if not self.active:
            self.active = True
            self.activation_time = time.monotonic()
            logger.info("[Nova] Wake phrase detected by openWakeWord.")
            print("[Nova] Wake phrase detected. Listening for command...")

    def process(self, text):
        text = text.strip()
        self.last_was_command = False

        if not text:
            return None

        # Handle a wake phrase detected in the transcription.
        if not self.active:
            if not self.contains_wake_phrase(text):
                return None

            command = self.remove_wake_phrase(text)
            self.active = True
            self.activation_time = time.monotonic()

            logger.info("[Nova] Wake phrase detected in transcription.")

            if not command:
                print("[Nova] Listening for command...")
                return None

            # Wake phrase and command were spoken together.
            self.last_was_command = True
            return self.execute_command(command)

        # Expire activation if the command doesn't arrive in time.
        if time.monotonic() - self.activation_time > COMMAND_TIMEOUT:
            logger.info("[Nova] Command timed out.")
            print("[Nova] Command timeout. Returning to normal listening.")
            self.active = False
            self.activation_time = 0.0

            # A new wake phrase can activate Nova again.
            if self.contains_wake_phrase(text):
                return self.process(text)

            return None

        # If the transcript contains only the wake phrase,
        # keep listening instead of sending it to the language model.
        command = (
            self.remove_wake_phrase(text)
            if self.contains_wake_phrase(text)
            else text
        )

        if not command:
            print("[Nova] Listening for command...")
            return None

        self.last_was_command = True
        logger.info("[Nova] Command received: %s", command)

        return self.execute_command(command)

    def execute_command(self, command):
        try:
            response = ask_nova(command)
            logger.info("Nova response: %s", response)
            return response

        except Exception as e:
            logger.exception("Nova Error: %s", e)
            return None

        finally:
            self.active = False
            self.activation_time = 0.0
