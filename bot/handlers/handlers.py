from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import NetworkError, TimedOut
import logging
from bot.utils.database import DatabaseIntern, DatabaseCourse, DatabaseJob
import os
import requests
import json
from bot.utils.logger import Logging
from dotenv import load_dotenv
from bot.utils.keywords_extraction import KeywordExtractor

load_dotenv()

Logging.setup_logging()

class HandlerMessage:
    def __init__(self):
        self.exctractor = KeywordExtractor()
        self.db_instances = {
            "magang": DatabaseIntern(),
            "course": DatabaseCourse(), 
            "jobs": DatabaseJob()
        }
        self.HF_TOKEN = os.getenv('HF_TOKEN')
        self.API_URL = os.getenv('API_URL')
        self.HEADERS = {
            "Authorization": f"Bearer {self.HF_TOKEN}",
            "Content-Type": "application/json"
        }

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
            "Arsitektur: GPT-2 kecil dengan 117M parameter\n"
            "Library: python-telegram-bot v20, Inference Providers (Featherless AI)\n\n"
            "Model ini dilatih terutama untuk SEA Region"
            "Sehingga mendukung bahasa Inggris, Indonesia, Vietnam, Thai, Tagalog, Malaysia, dsb."
        )
        await context.bot.send_message(chat_id=update.effective_chat.id, text=info_text)

    # Text-generating with SeaLLM
    async def stream_llm_response(self, messages: list, update: Update) -> str:
        payload = {
            "messages": messages,
            "model": "SeaLLMs/SeaLLMs-v3-7B-Chat",
            "stream": True
        }

        message = await update.message.reply_text("⌛ Generating...")
        full_response = ""

        try:
            with requests.post(self.API_URL, headers=self.HEADERS, json=payload, stream=True) as response:
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8').strip()
                        if decoded_line.startswith("data:"):
                            try:
                                chunk = json.loads(decoded_line[5:])
                                if chunk.get("choices"):
                                    content = chunk["choices"][0]["delta"].get("content", "")
                                    if content:
                                        full_response += content
                                        # Pastikan konten selalu berbeda
                                        await message.edit_text(full_response + "▌")
                            except json.JSONDecodeError:
                                continue

                # Hapus typing indicator (▌) di akhir
                await message.edit_text(full_response)
                
        except Exception as e:
            if "not modified" not in str(e):
                await message.edit_text(f"🚨 Error: {e}")
            error_msg = f"🚨 Error: {str(e)}"
            await message.edit_text(error_msg)
            return error_msg

    # Mendeteksi Intent untuk jenis permintaan user 
    async def detect_intent(self, input_user: str) -> str:
        prompt = f"""
        Klasifikasikan intent dari pesan berikut (jawab hanya dengan salah satu dari: magang, pekerjaan, kursus):
        Pesan: "{input_user}"
        """
        
        response = await self.query_llm(prompt)
        return response.lower().strip()

    # Mendeteksi dan mencari data yang ada di database untuk mengkonfigurasi ke LLM 
    async def search_data(self, intent: str, keyword: str, limit: int = 5):
        db_mapping = {
            "magang": self.db_instances["magang"],
            "pekerjaan": self.db_instances["jobs"],
            "kursus": self.db_instances["course"]
        }
        
        if intent not in db_mapping:
            return None
            
        results = db_mapping[intent].search(keyword=keyword, limit=limit)
        return results

    # Format data ke promt untuk LLM 
    def format_to_prompt(self, data: list) -> str:
        prompt = "Berikut rekomendasi berdasarkan database kami:\n"
        
        for idx, item in enumerate(data, 1):
            prompt += f"\n{idx}. {item['title']}\n"
            prompt += f"   Lokasi: {item.get('location', 'N/A')}\n"
            prompt += f"   Deskripsi: {item.get('description', '')[:100]}...\n"
        
        prompt += "\nBerikan respon dengan bahasa Indonesia yang natural dan tambahkan insight jika perlu:"
        return prompt

    # Membuat LLM untuk Generate Rekomendasi Job, Interns, Course
    async def generate_recommendation(self, user_input:str, update:Update):
        # Deteksi Intent Terlebih Dahulu 
        intent = await self.detect_intent(user_input)

        # Cari data ke dalam sebuah database yang telah diberikan
        keyword = self.exctractor.extract_keywords(user_input)  # Fungsi ekstraksi keyword
        data = await self.search_data(intent, keyword)

        data_prompt = self.format_to_prompt(data)

        full_prompt = f"""
        Anda adalah asisten karir. User mencari: "{user_input}".
        {data_prompt}
        """
        
        # Step 4: Generate response dengan SeaLLM
        return await self.stream_llm_response(
            messages=[{"role": "user", "content": full_prompt}],
            update=update
        )

    # Fungsi untuk menangani pesan pengguna dengan debugging
    async def handle_message(self,update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming Telegram messages with streaming"""
        user_input = update.message.text
        
        # Format messages for chat completion
        messages = [
            {"role": "system", "content": "Anda adalah asisten AI yang membantu dalam bahasa Indonesia. Berikan jawaban yang jelas dan ramah."},
            {"role": "user", "content": user_input}
        ]
        
        await self.stream_llm_response(messages, update)
    
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