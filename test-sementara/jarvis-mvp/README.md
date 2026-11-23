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

**Catatan:** Model `small` pada CPU bisa lambat. Untuk tes lebih ringan, ganti `MODEL_NAME = "small"` menjadi `MODEL_NAME = "base"` di `jarvis/app.py`. Akurasi bisa berkurang. Microphone perlu diizinkan di Windows Settings > Privacy & security > Microphone. Suara TTS Bahasa Indonesia bergantung voice Windows yang terpasang. UI menampilkan indikator volume microphone, deteksi suara berbasis ambang volume, dan hitung mundur 6 detik. Indikator ini bukan VAD atau waveform penuh; wake word belum tersedia.

Audio diproses lokal. Jangan commit rekaman, cache model, atau rahasia pribadi.

## Telegram bot v0.2 (opsional, desktop tidak berubah)

1. Buat bot melalui Telegram `@BotFather` dengan `/newbot`, simpan token secara privat.
2. Pastikan `ffmpeg -version` berjalan di Git Bash. Jika belum, instal FFmpeg dan tambahkan folder `bin` ke PATH Windows.
3. Di folder `jarvis-mvp`, jalankan `python -m pip install -r requirements.txt`.
4. Salin `.env.example` menjadi `.env` (`cp .env.example .env`) dan isi `TELEGRAM_BOT_TOKEN`. Jangan commit `.env`.
5. Jalankan `./.venv/Scripts/python.exe -m jarvis.telegram_bot`.
6. Chat bot dari akun Telegram sendiri, kirim `/id`, lalu isi angka ID tersebut ke `TELEGRAM_ALLOWED_USER_ID` dalam `.env`. Restart bot.
7. Kirim `/start`, `/chat` (balasan teks), atau `/voice` (balasan voice note). Kirim teks atau voice note berisi "Siapa gua?" untuk menguji.

Mode default adalah `/chat`; perubahan mode tersimpan selama proses bot hidup (reset saat restart). `/id` dapat dipakai sebelum whitelist disetel; command lainnya ditolak jika ID tidak cocok. Jangan bagikan token bot. Voice note maksimal 60 detik. Audio Telegram diunduh sementara, diproses Whisper lokal, lalu file sementara dihapus. Balasan voice dibuat memakai Windows TTS dan dikonversi ke OGG/Opus dengan FFmpeg. Kualitas suara mengikuti voice Windows. Telegram memerlukan internet dan bot harus tetap berjalan; desktop tetap dapat dijalankan dengan `python main.py` secara terpisah.
