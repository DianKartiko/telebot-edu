from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import NetworkError, TimedOut
import logging
from bot.utils.database import DatabaseIntern, DatabaseCourse, DatabaseJob
from bot.handlers.prompt_engine import PromptEngine
import os
from dotenv import load_dotenv

load_dotenv()

class HandlerMessage:
    def __init__(self):
        self.db_instances = {
            "magang": DatabaseIntern(),
            "course": DatabaseCourse(), 
            "jobs": DatabaseJob()
        }
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

    # Fungsi untuk menangani pesan pengguna dengan debugging
    async def handler_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_input = update.message.text
        chat_id = update.effective_chat.id
        
        # DEBUG: Log input pengguna
        logging.info(f"User input: {user_input}")
        
        try:
            parsed = self.prompt_engine.parse_input(user_input)
            # DEBUG: Log hasil parsing
            logging.info(f"Parsed result: {parsed}")
            
            # Validasi struktur parsed
            if not isinstance(parsed, dict) or 'intent' not in parsed:
                logging.error(f"Invalid parsed structure: {parsed}")
                await update.message.reply_text("❌ Format input tidak dapat dipahami")
                return

            intent = parsed['intent']
            # DEBUG: Log intent yang terdeteksi
            logging.info(f"Detected intent: {intent}")

            # Cek apakah intent valid
            if intent not in self.db_instances:
                logging.warning(f"Intent '{intent}' not found in db_instances")
                valid_intents = list(self.db_instances.keys())
                await update.message.reply_text(
                    f"❌ Intent tidak dikenali: '{intent}'\n"
                    f"Intent yang tersedia: {', '.join(valid_intents)}"
                )
                return

            db_instance = self.db_instances[intent]
            # DEBUG: Log database instance
            logging.info(f"Database instance: {type(db_instance).__name__}")
            
            method_name = f"search_{intent}"
            # DEBUG: Log method name yang dicari
            logging.info(f"Looking for method: {method_name}")
            
            # Cek apakah method exists
            search_method = getattr(db_instance, method_name, None)
            if not search_method:
                logging.error(f"Method {method_name} not found in {type(db_instance).__name__}")
                available_methods = [method for method in dir(db_instance) if not method.startswith('_')]
                await update.message.reply_text(
                    f"❌ Method '{method_name}' tidak ditemukan\n"
                    f"Method yang tersedia: {', '.join(available_methods)}"
                )
                return

            # DEBUG: Log parameter yang akan digunakan
            params = parsed.get("params", {})
            keyword = params.get("keyword", "")
            limit = int(os.getenv("MAX_RESULTS", 5))
            logging.info(f"Search parameters - keyword: '{keyword}', limit: {limit}")

            # Panggil method search
            logging.info(f"Calling {method_name} with keyword='{keyword}', limit={limit}")
            results = search_method(keyword=keyword, limit=limit)
            
            # DEBUG: Log hasil search
            logging.info(f"Search results count: {len(results) if results else 0}")
            if results:
                logging.info(f"First result sample: {results[0] if len(results) > 0 else 'None'}")
            else:
                logging.warning("No results returned from search")

            # Format dan kirim response
            if not results:
                await update.message.reply_text(f"❌ Tidak ada data {intent} yang ditemukan untuk keyword '{keyword}'")
                return

            response = self.prompt_engine.format_results(intent, results)
            # DEBUG: Log response yang akan dikirim
            logging.info(f"Response length: {len(response)}")
            
            await update.message.reply_text(response, parse_mode="HTML")

        except KeyError as e:
            logging.error(f"KeyError - Method tidak tersedia: {str(e)}", exc_info=True)
            await update.message.reply_text(f"🔧 KeyError: {str(e)} - Sedang dalam pengembangan")
        except AttributeError as e:
            logging.error(f"AttributeError - Attribute tidak ditemukan: {str(e)}", exc_info=True)
            await update.message.reply_text(f"🔧 AttributeError: Method tidak tersedia")
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}", exc_info=True)
            await update.message.reply_text(f"⚠️ Terjadi kesalahan sistem: {str(e)}")

    # Method untuk testing database connections
    async def test_databases(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Method untuk testing koneksi database"""
        test_results = []
        
        for intent, db_instance in self.db_instances.items():
            try:
                method_name = f"search_{intent}"
                search_method = getattr(db_instance, method_name, None)
                
                if search_method:
                    # Test dengan keyword kosong
                    results = search_method(keyword="", limit=1)
                    status = f"✅ {intent}: OK ({len(results) if results else 0} records)"
                else:
                    status = f"❌ {intent}: Method {method_name} tidak ditemukan"
                    
            except Exception as e:
                status = f"❌ {intent}: Error - {str(e)}"
            
            test_results.append(status)
        
        response = "🔧 **Test Database Connections:**\n\n" + "\n".join(test_results)
        await update.message.reply_text(response)

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