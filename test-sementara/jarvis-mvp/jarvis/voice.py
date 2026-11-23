"""Offline Indonesian transcription with live microphone level reporting."""
from pathlib import Path

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000
MODEL_CACHE = Path(__file__).resolve().parent.parent / "models" / "whisper-cache"
_model = None


def transcribe_once(model_path: str = "small", seconds: int = 6,
                    on_status=None, on_audio_level=None) -> str:
    global _model

    def report(message):
        if on_status:
            on_status(message)

    if _model is None:
        report("LOADING MODEL  •  DOWNLOAD PERTAMA BISA LAMA")
        MODEL_CACHE.mkdir(parents=True, exist_ok=True)
        _model = WhisperModel(
            model_path, device="cpu", compute_type="int8",
            download_root=str(MODEL_CACHE),
        )

    # Read 100 ms chunks so the UI can show a live volume meter.
    chunk_size = SAMPLE_RATE // 10
    chunks = []
    report("LISTENING  •  BICARA SEKARANG")
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32") as stream:
        for index in range(seconds * 10):
            chunk, overflowed = stream.read(chunk_size)
            chunks.append(chunk[:, 0].copy())
            rms = float(np.sqrt(np.mean(np.square(chunk[:, 0]))))
            # This is a simple volume indicator, not speech recognition.
            level = min(100, int(rms * 1200))
            if on_audio_level:
                on_audio_level(level, max(0, seconds * 10 - index - 1) / 10)
            if overflowed:
                report("LISTENING  •  AUDIO OVERFLOW, LANJUTKAN")

    if on_audio_level:
        on_audio_level(0, 0)
    report("PROCESSING  •  MENGENALI SUARA")
    recording = np.concatenate(chunks).astype(np.float32, copy=False)
    segments, _ = _model.transcribe(
        recording, language="id", beam_size=3, vad_filter=True,
    )
    return " ".join(s.text.strip() for s in segments).strip()
