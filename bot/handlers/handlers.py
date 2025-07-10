from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import NetworkError, TimedOut
from dotenv import load_dotenv
import logging
# Import Own Library
from bot.utils.logger import Logging
from bot.utils.llm_integration import LLMIntegration

load_dotenv()

Logging.setup_logging()

class HandlerMessage:
    def __init__(self):
        self.llm = LLMIntegration()
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
/info - informasi bot telegram

**Contoh Custom Prompt:**
"Tampilkan lowongan magang bidang TI di Bandung"
"Kursus tersedia untuk pemula di bidang keuangan"
        '''
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    # Fungsi Info
    async def info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        info_text = (
"🤖 Informasi Teknis:\n\n"
"Model: SeaLLMs/SeaLLMs-v3-7B-Chat\n"
"Arsitektur: Menggunakan model dari qwen2 dengan 7.62B params\n"
"Library & Teknologi: python-telegram-bot v20 (Library), Inference Providers (Featherless AI)\n\n"
"Model ini dilatih terutama untuk SEA Region.\n"
"Mendukung multibahasa seperti bahasa Inggris, Indonesia, Vietnam, Thai, Tagalog, Malaysia, dsb."
        )
        await context.bot.send_message(chat_id=update.effective_chat.id, text=info_text)

    # Fungsi untuk menangani pesan pengguna dengan debugging
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            user_input = update.message.text
            response = await self.llm.process_user_request(user_input, update)
            
            # Fallback jika response kosong
            if not response.strip():
                response = "⚠️ Maaf, terjadi kesalahan internal."
                
            # Hanya kirim jika belum dikirim via streaming
            if not context.chat_data.get("has_replied"):
                await update.message.reply_text(response)
                context.chat_data["has_replied"] = True
            
        except Exception as e:
            logging.error(f"Error in handler: {str(e)}")
            await update.message.reply_text("⚠️ Sistem sedang sibuk, coba lagi nanti.")
            
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