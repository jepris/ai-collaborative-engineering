"""Audio conversion and speech for Telegram; requires ffmpeg on PATH."""
import subprocess
import wave
from pathlib import Path

import numpy as np
import pyttsx3

from jarvis.voice import MODEL_CACHE
from faster_whisper import WhisperModel

_model = None


def _ffmpeg(*args):
    try:
        subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y", *map(str, args)],
                       check=True, capture_output=True, timeout=90)
    except FileNotFoundError as exc:
        raise RuntimeError("FFmpeg belum tersedia di PATH. Install FFmpeg lalu buka terminal baru.") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("FFmpeg gagal memproses audio: " + exc.stderr.decode(errors="replace")[-500:]) from exc


def transcribe_voice(source: Path, wav_path: Path) -> str:
    global _model
    _ffmpeg("-i", source, "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", wav_path)
    with wave.open(str(wav_path), "rb") as audio:
        samples = np.frombuffer(audio.readframes(audio.getnframes()), dtype=np.int16)
    if _model is None:
        MODEL_CACHE.mkdir(parents=True, exist_ok=True)
        _model = WhisperModel("small", device="cpu", compute_type="int8",
                              download_root=str(MODEL_CACHE))
    segments, _ = _model.transcribe(samples.astype(np.float32) / 32768.0,
                                    language="id", beam_size=3, vad_filter=True)
    return " ".join(segment.text.strip() for segment in segments).strip()


def make_voice(text: str, wav_path: Path, ogg_path: Path) -> None:
    engine = pyttsx3.init(driverName="sapi5")
    try:
        engine.setProperty("rate", 165)
        engine.save_to_file(text, str(wav_path))
        engine.runAndWait()
    finally:
        engine.stop()
    if not wav_path.exists() or wav_path.stat().st_size == 0:
        raise RuntimeError("Windows TTS gagal membuat file audio.")
    _ffmpeg("-i", wav_path, "-c:a", "libopus", "-b:a", "32k", "-application", "voip", ogg_path)
