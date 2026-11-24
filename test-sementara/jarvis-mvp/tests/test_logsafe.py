"""Run from test-sementara/jarvis-mvp: python -m unittest tests.test_logsafe -v"""
import io
import logging
import unittest

from jarvis.logsafe import RedactingFormatter

TOKEN = "123456789:AAFakeTokenForTestOnly_abc"


def _log(formatter: RedactingFormatter, fn) -> str:
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(formatter)
    logger = logging.getLogger(f"logsafe-test-{id(stream)}")
    logger.propagate = False
    logger.addHandler(handler)
    fn(logger)
    return stream.getvalue()


class RedactingFormatterTest(unittest.TestCase):
    def test_token_masked_in_message_and_traceback(self):
        def emit(logger):
            try:
                raise RuntimeError(f"GET https://api.telegram.org/bot{TOKEN}/getMe failed")
            except RuntimeError:
                logger.exception("request to https://api.telegram.org/bot%s/getMe", TOKEN)

        out = _log(RedactingFormatter(TOKEN), emit)
        self.assertNotIn(TOKEN, out)
        self.assertIn("bot***/getMe", out)

    def test_empty_secret_leaves_text_unchanged(self):
        out = _log(RedactingFormatter(""), lambda logger: logger.error("plain message"))
        self.assertTrue(out.strip().endswith(":plain message"))


if __name__ == "__main__":
    unittest.main()
