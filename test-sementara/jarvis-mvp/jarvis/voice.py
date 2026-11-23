"""Offline Indonesian transcription with multilingual Whisper."""
from pathlib import Path

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000
MODEL_CACHE = Path(__file__).resolve().parent.parent / "models" / "whisper-cache"
_model = None

def transcribe_once(model_path: str = "small", seconds: int = 6, on_status=None) -> str:
    def report(message):
        if on_status:
            on_status(message)

    global _model
    if _model is None:
        report("LOADING MODEL  •  DOWNLOAD PERTAMA BISA LAMA")
        MODEL_CACHE.mkdir(parents=True, exist_ok=True)
        _model = WhisperModel(model_path, device="cpu", compute_type="int8", download_root=str(MODEL_CACHE))
    report("LISTENING  •  BICARA SEKARANG (6 DETIK)")
    recording = sd.rec(int(seconds * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="float32")
    sd.wait()
    report("PROCESSING  •  MENGENALI SUARA")
    segments, _ = _model.transcribe(np.asarray(recording[:, 0], dtype=np.float32), language="id", beam_size=3, vad_filter=True)
    return " ".join(s.text.strip() for s in segments).strip()
