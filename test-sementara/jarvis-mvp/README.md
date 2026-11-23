# Jarvis Desktop MVP v0.1

Aplikasi desktop Windows untuk mengenali perintah suara Bahasa Indonesia secara offline dan membalas menggunakan Windows Text-to-Speech. **Tidak memakai AI API.**

## Persyaratan

- Windows 10/11
- Python 3.11 atau 3.12 (64-bit) direkomendasikan
- Microphone dan speaker
- Internet sekali untuk menginstal dependency dan mengunduh model STT

## Instalasi (PowerShell)

Buka PowerShell di folder `jarvis-mvp`, kemudian:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Jika Python 3.11 tidak tersedia, gunakan `py -3.12` jika terpasang. Jika PowerShell menolak aktivasi virtual environment, gunakan `cmd.exe` dan `.venv\Scripts\activate.bat`.

## Download model Bahasa Indonesia

1. Buka https://alphacephei.com/vosk/models
2. Cari model **Bahasa Indonesia** (misalnya `vosk-model-small-id-0.22` jika masih tersedia).
3. Unduh ZIP model dan ekstrak isinya.
4. **Rename folder hasil ekstrak menjadi `vosk-id`**, dan taruh di dalam folder `models`.

Struktur yang diharapkan:

```text
jarvis-mvp/
  models/
    vosk-id/
      am/
      conf/
      graph/
      ...
```

Model tidak disertakan di repository karena ukurannya besar. Pastikan folder `models/vosk-id` berisi file model langsung, bukan satu folder tambahan.

## Jalankan

```powershell
python main.py
```

Tekan tombol **MULAI DENGARKAN**, ucapkan satu kalimat, lalu tunggu hingga jendela menampilkan transkrip dan Jarvis membalas dengan suara. Durasi rekam awal adalah 6 detik.

Contoh perintah:

| Ucapan | Jawaban |
|---|---|
| Siapa gua? | Anda adalah Ibnu, Master. |
| Halo Jarvis | Halo Master, saya siap membantu. |
| Siapa kamu? | Saya Jarvis, asisten pribadi Anda. |

## Batasan MVP

- UI visual HUD sederhana, belum ada visualizer waveform sungguhan.
- Perekaman berlangsung 6 detik per klik, belum ada VAD atau wake word.
- Model STT dapat keliru menangkap kata informal seperti "gua"; lihat transkrip di layar.
- Windows voice Indonesia mungkin belum tersedia; pyttsx3 memakai voice Windows yang terpasang.
- Model Vosk di-load setiap kali tombol ditekan; respons awal dapat lebih lambat. Optimalisasi cache model menyusul.
- Aplikasi belum dikemas menjadi installer.

## Privasi

Audio diproses lokal oleh Vosk. Tidak ada audio yang dikirim ke Gemini/OpenAI. Jangan commit model, rekaman, atau data sensitif ke GitHub.

## Struktur

- `main.py` — entry point
- `jarvis/app.py` — PySide6 GUI dan worker thread
- `jarvis/voice.py` — microphone dan Vosk STT
- `jarvis/commands.py` — respons perintah sederhana
- `jarvis/tts.py` — suara balasan Windows
- `models/` — tempat model Vosk yang diunduh sendiri
