from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import NetworkError, TimedOut, BadRequest
from dotenv import load_dotenv
import logging
# Import Own Library
from bot.utils.logger import Logging
from bot.utils.llm_integration import EnhancedLLMIntegration

load_dotenv()

Logging.setup_logging()

class HandlerMessage:
    def __init__(self):
        self.llm = EnhancedLLMIntegration()
    
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

    # Fungsi untuk menangani pesan pengguna dengan enhanced handling
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Enhanced message handler dengan error handling yang lebih baik
        dan integrasi dengan EnhancedLLMIntegration
        """
        # Validasi input dasar
        if not update or not update.message or not update.message.text:
            await update.message.reply_text("⚠️ Pesan tidak valid. Silakan kirim pesan teks.")
            return
        
        # Validasi user
        if not update.effective_user:
            await update.message.reply_text("⚠️ Tidak dapat mengidentifikasi pengguna.")
            return
        
        # Reset has_replied flag untuk pesan baru
        context.chat_data["has_replied"] = False
        
        try:
            user_input = update.message.text.strip()
            
            # Validasi input tidak kosong
            if not user_input:
                await update.message.reply_text("⚠️ Pesan tidak boleh kosong. Silakan kirim pertanyaan yang jelas.")
                return
            
            # Validasi panjang input (untuk menghindari spam)
            if len(user_input) > 1000:
                await update.message.reply_text("⚠️ Pesan terlalu panjang. Maksimal 1000 karakter.")
                return
            
            # Log user input untuk debugging
            logging.info(f"User {update.effective_user.id} sent: {user_input[:100]}...")
            
            # Process dengan EnhancedLLMIntegration
            # Note: generate_response di EnhancedLLMIntegration sudah handle sending message
            response = await self.llm.process_user_request(user_input, update)
            
            # Validasi response
            if not response or not response.strip():
                fallback_response = "⚠️ Maaf, tidak dapat memproses permintaan Anda saat ini. Silakan coba lagi."
                if not context.chat_data.get("has_replied"):
                    await update.message.reply_text(fallback_response)
                    context.chat_data["has_replied"] = True
                return fallback_response
            
            # Jika response belum dikirim via streaming di LLM (fallback)
            if not context.chat_data.get("has_replied"):
                await update.message.reply_text(response)
                context.chat_data["has_replied"] = True
            
            # Log successful response
            logging.info(f"Response sent to user {update.effective_user.id}: {len(response)} chars")
            
            return response
            
        except NetworkError as e:
            error_msg = "🌐 Masalah koneksi. Silakan coba lagi dalam beberapa saat."
            logging.error(f"Network error for user {update.effective_user.id}: {str(e)}")
            await self._send_error_message(update, context, error_msg)
            
        except TimedOut as e:
            error_msg = "⏱️ Permintaan timeout. Silakan coba dengan pertanyaan yang lebih sederhana."
            logging.error(f"Timeout error for user {update.effective_user.id}: {str(e)}")
            await self._send_error_message(update, context, error_msg)
            
        except BadRequest as e:
            error_msg = "❌ Format pesan tidak valid. Silakan coba lagi."
            logging.error(f"Bad request for user {update.effective_user.id}: {str(e)}")
            await self._send_error_message(update, context, error_msg)
            
        except ValueError as e:
            error_msg = "⚠️ Input tidak valid. Silakan periksa format pertanyaan Anda."
            logging.error(f"Value error for user {update.effective_user.id}: {str(e)}")
            await self._send_error_message(update, context, error_msg)
            
        except Exception as e:
            error_msg = "🚨 Terjadi kesalahan sistem. Tim teknis sedang memperbaiki."
            logging.error(f"Unexpected error for user {update.effective_user.id}: {str(e)}", exc_info=True)
            await self._send_error_message(update, context, error_msg)
    
    async def _send_error_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, error_msg: str):
        """Helper method untuk mengirim pesan error"""
        try:
            if not context.chat_data.get("has_replied"):
                full_error_msg = f"{error_msg}\n\n💡 Gunakan /help untuk panduan atau /start untuk memulai ulang."
                await update.message.reply_text(full_error_msg)
                context.chat_data["has_replied"] = True
        except Exception as send_error:
            logging.error(f"Failed to send error message: {str(send_error)}")
            # Fallback: try to send simple message
            try:
                await update.message.reply_text("⚠️ Sistem sedang bermasalah. Silakan coba lagi.")
            except Exception as fallback_error:
                logging.error(f"Failed to send fallback message: {str(fallback_error)}")
            
    # Fungsi error handler yang lebih comprehensive
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced error handler dengan logging dan user feedback yang lebih baik"""
        
        # Log error dengan detail
        logging.error(
            f'Exception while handling update {update.update_id if update else "Unknown"}: {context.error}',
            exc_info=context.error
        )

        # Jika update tidak valid, tidak bisa mengirim pesan
        if not update or not hasattr(update, 'effective_message') or not update.effective_message:
            logging.error("Invalid update object, cannot send error message to user")
            return

        error = context.error
        user_message = "⚠️ Maaf, terjadi kesalahan."

        # Kategorisasi error berdasarkan tipe
        if isinstance(error, NetworkError):
            user_message = "🌐 Masalah koneksi jaringan. Silakan coba lagi dalam beberapa saat."
        elif isinstance(error, TimedOut):
            user_message = "⏱️ Waktu respons habis. Silakan coba dengan pertanyaan yang lebih sederhana."
        elif isinstance(error, BadRequest):
            user_message = "❌ Format permintaan tidak valid. Silakan periksa input Anda."
        elif isinstance(error, ValueError):
            user_message = "⚠️ Input tidak valid. Silakan coba dengan format yang berbeda."
        elif isinstance(error, IndexError):
            user_message = "📝 Terjadi kesalahan dalam pemrosesan data. Silakan coba lagi."
        elif "rate limit" in str(error).lower():
            user_message = "🚦 Terlalu banyak permintaan. Silakan tunggu sebentar sebelum mencoba lagi."
        elif "timeout" in str(error).lower():
            user_message = "⏱️ Sistem sedang lambat. Silakan coba lagi dalam beberapa saat."
        else:
            user_message = "🚨 Terjadi kesalahan sistem. Tim teknis sedang memperbaiki."

        # Kirim pesan error ke user
        try:
            full_message = f"{user_message}\n\n💡 Gunakan /help untuk panduan atau /start untuk memulai ulang."
            await update.effective_message.reply_text(full_message)
            
        except Exception as send_error:
            logging.error(f'Failed to send error message to user: {str(send_error)}')
            
            # Fallback: coba kirim pesan sederhana
            try:
                await update.effective_message.reply_text("⚠️ Sistem bermasalah. Silakan coba lagi.")
            except Exception as fallback_error:
                logging.error(f'Failed to send fallback error message: {str(fallback_error)}')

        # Log statistik error untuk monitoring
        error_type = type(error).__name__
        user_id = update.effective_user.id if update.effective_user else "Unknown"
        logging.info(f"Error handled: {error_type} for user {user_id}")