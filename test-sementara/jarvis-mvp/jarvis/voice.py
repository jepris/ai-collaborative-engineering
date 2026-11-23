"""Audio capture and offline speech recognition; runs outside the UI thread."""
import json
import queue
import time

import sounddevice as sd
from vosk import KaldiRecognizer, Model

SAMPLE_RATE = 16000


def transcribe_once(model_path: str, seconds: int = 6) -> str:
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, SAMPLE_RATE)
    chunks: queue.Queue[bytes] = queue.Queue()

    def callback(indata, frames, time_info, status):
        if status:
            # Audio overflow/underflow should not crash the UI.
            pass
        chunks.put(bytes(indata))

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE, blocksize=4000, dtype="int16", channels=1,
        callback=callback,
    ):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            try:
                data = chunks.get(timeout=min(0.25, max(0.01, deadline - time.monotonic())))
            except queue.Empty:
                continue
            recognizer.AcceptWaveform(data)
    result = json.loads(recognizer.FinalResult())
    return result.get("text", "").strip()
