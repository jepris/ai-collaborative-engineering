"""Offline Indonesian transcription with multilingual Whisper."""
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000
_model = None

def transcribe_once(model_path: str = "small", seconds: int = 6) -> str:
    global _model
    if _model is None:
        _model = WhisperModel(model_path, device="cpu", compute_type="int8")
    recording = sd.rec(int(seconds * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="float32")
    sd.wait()
    segments, _ = _model.transcribe(np.asarray(recording[:, 0], dtype=np.float32), language="id", beam_size=3, vad_filter=True)
    return " ".join(s.text.strip() for s in segments).strip()
