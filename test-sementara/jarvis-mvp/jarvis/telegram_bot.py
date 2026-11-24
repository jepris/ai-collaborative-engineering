"""Telegram transport for Jarvis. Run separately: python -m jarvis.telegram_bot."""
import asyncio
import logging
import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.error import NetworkError, RetryAfter
from telegram.ext import (
    Application, ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters,
)

from jarvis.commands import handle_command
from jarvis.logsafe import RedactingFormatter
from jarvis.telegram_audio import make_voice, transcribe_voice

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
ALLOWED_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_ID", "").strip()
MODES = {}
logger = logging.getLogger(__name__)

# shortcut: fixed 30 s timeout and 2 startup retries, raise only if the network stays this slow.
NETWORK_TIMEOUT = 30
BOOTSTRAP_RETRIES = 2


def authorized(update: Update) -> bool:
    return bool(ALLOWED_USER_ID and update.effective_user
                and str(update.effective_user.id) == ALLOWED_USER_ID)


async def require_access(update: Update) -> bool:
    if authorized(update):
        return True
    if update.effective_message:
        await update.effective_message.reply_text(
            "Akses ditolak. Untuk setup, gunakan /id dan masukkan ID Anda ke .env."
        )
    return False


async def show_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        f"Telegram User ID Anda: {update.effective_user.id}\n"
        "Simpan sebagai TELEGRAM_ALLOWED_USER_ID di .env lokal."
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_access(update):
        return
    await update.effective_message.reply_text(
        "Jarvis siap, Master. Gunakan /chat untuk balasan teks atau /voice untuk balasan suara. "
        "Kirim teks atau voice note. Mode awal: /chat."
    )


async def set_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_access(update):
        return
    mode = update.effective_message.text.split()[0].split("@")[0][1:]
    MODES[update.effective_user.id] = mode
    await update.effective_message.reply_text(
        f"Mode {mode} aktif, Master. "
        + ("Saya akan membalas dengan voice message." if mode == "voice"
           else "Saya akan membalas dengan teks.")
    )


async def reply_with_mode(update: Update, response: str):
    if MODES.get(update.effective_user.id, "chat") != "voice":
        await update.effective_message.reply_text(response)
        return
    with tempfile.TemporaryDirectory(prefix="jarvis-tg-") as tmp:
        wav_path = Path(tmp) / "reply.wav"
        ogg_path = Path(tmp) / "reply.ogg"
        await asyncio.to_thread(make_voice, response, wav_path, ogg_path)
        with ogg_path.open("rb") as audio:
            await update.effective_message.reply_voice(voice=audio)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_access(update):
        return
    message = update.effective_message
    try:
        if message.voice:
            if message.voice.duration > 60:
                await message.reply_text("Voice note maksimal 60 detik untuk MVP.")
                return
            await message.reply_text("Voice diterima, sedang diproses...")
            with tempfile.TemporaryDirectory(prefix="jarvis-tg-") as tmp:
                source = Path(tmp) / "incoming.ogg"
                wav = Path(tmp) / "incoming.wav"
                tg_file = await context.bot.get_file(message.voice.file_id)
                await tg_file.download_to_drive(custom_path=source)
                transcript = await asyncio.to_thread(transcribe_voice, source, wav)
            if not transcript:
                await message.reply_text("Maaf Master, suara belum terbaca.")
                return
        else:
            transcript = message.text or ""
        response = handle_command(transcript)
        await reply_with_mode(update, response)
    except Exception:
        logger.exception("Telegram message processing failed")
        await message.reply_text("Maaf Master, proses gagal. Periksa terminal bot untuk detail error.")


async def on_startup(app: Application) -> None:
    # Runs only after getMe succeeded, unlike a print placed before run_polling.
    print(f"Jarvis Telegram bot terhubung sebagai @{app.bot.username}. Tekan Ctrl+C untuk berhenti.")


def main():
    handler = logging.StreamHandler()
    handler.setFormatter(RedactingFormatter(TOKEN))
    logging.basicConfig(level=logging.INFO, handlers=[handler])
    # httpx logs request URLs (which contain the token) at INFO; the formatter above is the backstop.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    if not TOKEN:
        raise SystemExit("Isi TELEGRAM_BOT_TOKEN di file .env terlebih dahulu.")
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .connect_timeout(NETWORK_TIMEOUT)
        .read_timeout(NETWORK_TIMEOUT)
        .write_timeout(NETWORK_TIMEOUT)
        .get_updates_connect_timeout(NETWORK_TIMEOUT)
        .get_updates_read_timeout(NETWORK_TIMEOUT)
        .post_init(on_startup)
        .build()
    )
    app.add_handler(CommandHandler("id", show_id))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("chat", set_mode))
    app.add_handler(CommandHandler("voice", set_mode))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND | filters.VOICE, handle_message))
    try:
        app.run_polling(drop_pending_updates=True, bootstrap_retries=BOOTSTRAP_RETRIES)
    except RetryAfter as exc:
        raise SystemExit(f"Telegram membatasi request (429). Tunggu {exc.retry_after} detik, lalu jalankan ulang satu kali.") from None
    except NetworkError:
        raise SystemExit("Koneksi ke Telegram gagal atau timeout. Periksa jaringan, lalu jalankan ulang satu kali (jangan di-loop).") from None


if __name__ == "__main__":
    main()
