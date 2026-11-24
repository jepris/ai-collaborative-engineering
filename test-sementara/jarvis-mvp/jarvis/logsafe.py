"""Log formatter that masks secrets (bot token) in the final text, tracebacks included."""
import logging


class RedactingFormatter(logging.Formatter):
    def __init__(self, *secrets: str):
        super().__init__("%(levelname)s:%(name)s:%(message)s")
        self.secrets = [s for s in secrets if s]  # empty secret would mask every character gap

    def format(self, record: logging.LogRecord) -> str:
        text = super().format(record)
        for secret in self.secrets:
            text = text.replace(secret, "***")
        return text
