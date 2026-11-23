# Log Chat — Test Sementara

**Repository:** `jepris/ai-collaborative-engineering`  
**Folder:** `test-sementara/`  
**Tujuan:** Catatan sementara untuk menguji alur kolaborasi ChatGPT, Master, dan GitHub.

---

## 2026-11-24

### ChatGPT — Catatan 1

- Master meminta dibuatkan folder khusus untuk percakapan ini dengan nama `test-sementara`.
- Folder berisi satu file catatan, yaitu `log.md`.
- Folder dan file dibuat langsung di branch `main` melalui GitHub.
- Catatan ini bersifat sementara untuk keperluan pengujian.

### Status

- [x] Folder `test-sementara/` dibuat.
- [x] File `log.md` dibuat.


### ChatGPT — Catatan 2: Jarvis Desktop MVP v0.1

**Tanggal:** 2026-11-24  
**Status:** SOURCE_COMMITTED — belum diuji pada Windows Master

- Master memilih desktop Windows sebagai platform MVP awal.
- MVP tidak memerlukan Gemini maupun OpenAI API; perintah dijawab melalui aturan lokal.
- Teknologi awal: Python, PySide6, Vosk, sounddevice, pyttsx3 / Windows SAPI.
- Source code ditambahkan ke `test-sementara/jarvis-mvp/`.
- File mencakup `main.py`, `requirements.txt`, `README.md`, `.gitignore`, dan modul `jarvis/app.py`, `voice.py`, `commands.py`, `tts.py`.
- Perintah uji: "Siapa gua?", "Halo Jarvis", dan "Siapa kamu?".
- Model Vosk Bahasa Indonesia perlu diunduh terpisah ke `models/vosk-id/`.
- UI, microphone, STT, dan TTS belum diverifikasi di perangkat Master.
- Commit source terakhir: `7301831af688b800e70aed994f2b6c040a19bf39`.

**Langkah berikutnya:** Master menjalankan `git pull origin main`, memasang dependencies dan model Vosk, lalu menguji perintah suara di Windows.

### Status terbaru

- [x] Source Jarvis MVP v0.1 tersedia di GitHub.
- [x] Dokumentasi instalasi tersedia di `test-sementara/jarvis-mvp/README.md`.
- [ ] Pengujian microphone dan speech-to-text di Windows.
- [ ] Pengujian balasan suara Windows TTS.
- [ ] Evaluasi hasil pengujian dan perbaikan.
