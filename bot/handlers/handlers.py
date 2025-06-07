from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import NetworkError, TimedOut
import logging
from bot.utils.database import DatabaseIntern
from bot.handlers.prompt_engine import PromptEngine
import os
from dotenv import load_dotenv

load_dotenv()

class HandlerMessage:
    def __init__(self):
        self.db = DatabaseIntern()
        self.prompt_engine = PromptEngine()

    # Fungsi Untuk Menjalankan Bot
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = '''
🤖 Halo! Selamat datang di Virtual Assistant Bot!

Saya asisten digital yang siap membantu Anda mencari informasi tentang:
🔹 Lowongan magang
🔹 Peluang pekerjaan
🔹 Rekomendasi kursus/keterampilan

📢 Penting untuk diketahui:
Saya masih dalam tahap pengembangan aktif dan terus belajar. Saat ini saya memiliki beberapa keterbatasan:
- Jawaban mungkin belum sempurna (terutama dalam Bahasa Indonesia)
- Belum bisa memahami semua jenis pertanyaan
- Kadang merespon dengan kurang akurat

💪 Tim developer saat ini sedang bekerja keras untuk meningkatkan kemampuan saya setiap hari!

💡 Tips: Gunakan kalimat sederhana dan kata kunci jelas untuk hasil terbaik.
'''
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    # Fungsi Help
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = '''
**📌 Bantuan Penggunaan Bot**

**Perintah Tersedia:**
/start - Untuk memulai bot
/help - Tampilkan menu bantuan

**Contoh Custom Prompt:**
"Tampilkan lowongan magang bidang TI di Bandung"
"Kursus tersedia untuk pemula di bidang keuangan"
'''
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    # Fungsi Info
    async def info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        info_text = (
            "🤖 Informasi Teknis:\n\n"
            "Model: Microsoft DialoGPT-small\n"
            "Arsitektur: GPT-2 kecil dengan 117M parameter\n"
            "Library: python-telegram-bot v20, Transformers, Torch\n\n"
            "Model ini dilatih terutama untuk bahasa Inggris, "
            "tetapi sudah dimodifikasi untuk memahami konteks bahasa Indonesia."
        )
        await context.bot.send_message(chat_id=update.effective_chat.id, text=info_text)

    # Fungsi untuk menangani pesan pengguna
    async def handler_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_input = update.message.text
        chat_id = update.effective_chat.id

        parsed = self.prompt_engine.parse_input(user_input)

        if not parsed["intent"]:
            await update.message.reply_text("ℹ️ Ketik 'magang' untuk mulai mencari.")
            return

        # Cari di database
        results = self.db.search_magang(
            keyword=parsed["params"].get("keyword"),
            limit=int(os.getenv("MAX_RESULTS", 5))
        )

        # Format dan kirim hasil
        response = self.prompt_engine.format_results(parsed["intent"], results)
        await update.message.reply_text(response, parse_mode="HTML")

    # Fungsi error handler
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logging.error('Exception while handling an update:', exc_info=context.error)

        if not update or not hasattr(update, 'effective_message'):
            return

        error = context.error
        user_message = "Maaf, terjadi kesalahan."

        if isinstance(error, NetworkError):
            user_message = "Masalah koneksi. Tolong coba lagi nanti."
        elif isinstance(error, TimedOut):
            user_message = "Waktu respon habis. Mohon coba lagi."
        elif isinstance(error, ValueError):
            user_message = "Input tidak valid. Silakan coba input yang berbeda."
        elif isinstance(error, IndexError):
            user_message = "Terjadi kesalahan dalam pemrosesan data."

        try:
            await update.effective_message.reply_text(
                f"{user_message}\n\nGunakan /help untuk bantuan dan /start untuk memulai kembali."
            )
        except Exception as e:
            logging.error('Gagal mengirim pesan error:', exc_info=e)
