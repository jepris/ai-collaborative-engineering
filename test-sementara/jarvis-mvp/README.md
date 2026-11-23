# Jarvis Desktop MVP v0.1 — Whisper Local

Aplikasi Windows untuk mengenali perintah Bahasa Indonesia dan membalas dengan suara. Tanpa AI API.

## Instalasi (PowerShell)

Python 3.11 atau 3.12 64-bit direkomendasikan.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

Tidak perlu mengunduh model Vosk. Model multilingual Whisper `small` diunduh otomatis saat pertama kali digunakan (internet diperlukan, ukuran beberapa ratus MB), lalu tersimpan di folder project `models/whisper-cache/` (diabaikan oleh Git). Pemakaian berikutnya dapat offline jika model sudah tersedia.

Tekan **MULAI DENGARKAN (6 DETIK)** lalu ucapkan "Siapa gua?", "Halo Jarvis", atau "Siapa kamu?". Jarvis menampilkan transkrip dan membalas melalui Windows TTS.

**Catatan:** Model `small` pada CPU bisa lambat. Untuk tes lebih ringan, ganti `MODEL_NAME = "small"` menjadi `MODEL_NAME = "base"` di `jarvis/app.py`. Akurasi bisa berkurang. Microphone perlu diizinkan di Windows Settings > Privacy & security > Microphone. Suara TTS Bahasa Indonesia bergantung voice Windows yang terpasang. UI masih sederhana; belum ada waveform atau wake word.

Audio diproses lokal. Jangan commit rekaman, cache model, atau rahasia pribadi.
