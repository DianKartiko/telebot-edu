import os 
from dotenv import load_dotenv
from typing import List, Dict
from bot.utils.database import DatabaseJob, DatabaseCourse, DatabaseIntern
from telegram import Update
import requests
import json
from bot.utils.keywords_extraction import KeywordExtractor
import sqlite3

load_dotenv()

class LLMIntegration:
    """Handler untuk integrasi SeaLLM"""
    def __init__(self):
        self.HF_TOKEN = os.getenv('HF_TOKEN')
        self.API_URL = os.getenv('API_URL')
        self.HEADERS = {
            "Authorization": f"Bearer {self.HF_TOKEN}",
            "Content-Type": "application/json"
        }
        self.db_job = DatabaseJob()
        self.db_course = DatabaseCourse()
        self.db_intern = DatabaseIntern()
        self.extractor = KeywordExtractor()

    # Untuk Mengenerate Respon secara realtime dengan menggunakan SeaLLM
    async def generate_response(self, messages: List[dict], update: Update) -> str:
        payload = {
            "messages": messages,
            "model": "SeaLLMs/SeaLLMs-v3-7B-Chat",
            "stream": True,
            "max_tokens": 500
        }

        # Kirim pesan loading
        loading_msg = await update.message.reply_text("Generate Response...")
        full_response = ""

        try:
            with requests.post(self.API_URL, headers=self.HEADERS, json=payload, stream=True) as response:
                response.raise_for_status()
                
                has_content = False
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8').strip()
                        if decoded_line.startswith("data:"):
                            try:
                                chunk = json.loads(decoded_line[5:])
                                if chunk.get("choices"):
                                    content = chunk["choices"][0]["delta"].get("content", "")
                                    if content:
                                        has_content = True
                                        full_response += content
                                        if len(full_response) % 5 == 0:
                                            try:
                                                await loading_msg.edit_text(full_response + "▌")
                                            except:
                                                pass
                            except json.JSONDecodeError:
                                continue

                # Handle empty response
                if not has_content:
                    full_response = "⚠️ Tidak mendapatkan respons dari AI. Coba lagi nanti."
                
                await loading_msg.edit_text(full_response)
                return full_response

        except Exception as e:
            error_msg = f"🚨 Error: {str(e)[:200]}"
            await loading_msg.edit_text(error_msg)
            return error_msg

        return str(full_response) if full_response else "⚠️ Respons kosong dari AI"
    
    # Memproses user request dengan mencari keywords yang tepat dan sesuai
    async def process_user_request(self, user_input: str, update: Update) -> str:
        try:
            # Validasi input
            if not user_input.strip():
                return "❌ Pesan tidak boleh kosong"

            # Ekstrak kata kunci
            keywords = self.extractor.extract(user_input)
            
            # Query database
            items = []
            if keywords["intent"] == "magang":
                items = self.db_intern.search_magang(keywords["field"], keywords["location"])
            elif keywords["intent"] == "pekerjaan":
                items = self.db_job.search_jobs(keywords["field"], keywords["location"])
            elif keywords["intent"] == "course":
                items = self.db_course.search_course(keywords["field"])
            else: 
                items = self.db_intern.search_magang(keyword=" ".join(keywords["field"]))
                items = self.db_job.search_jobs(keyword=" ".join(keywords["field"]))
                items = self.db_course.search_course(keyword=" ".join(keywords["field"]))

            # Handle empty results
            if not items:
                return "🔍 Tidak ditemukan hasil. Coba gunakan kata kunci lain."

            # Bangun prompt
            prompt = self._build_prompt(user_input, keywords, items)
            if not prompt.strip():
                return "⚠️ Gagal membangun prompt."

            # Generate response
            return await self.generate_response(
                messages=[{"role": "user", "content": prompt}],
                update=update
            )

        except Exception as e:
            return f"⚠️ Terjadi error: {str(e)[:200]}"
        
    def _build_prompt(self, user_input: str, keywords: Dict, items: List[Dict]) -> str:
        """Format data untuk prompt LLM"""
        items_str = "\n".join(
            f"{idx+1}. {self._get_item_title(item, keywords['intent'])} - {item.get('penyelenggara', 'N/A')}\n"
            f"   Lokasi: {item.get('lokasi', 'N/A')}\n"
            f"   Deskripsi: {item.get('deskripsi', '')[:100]}...\n"
            for idx, item in enumerate(items)
        )
        
        return f"""
        User mencari: "{user_input}"
        Rekomendasi dari database:
        {items_str}

        Instruksi:
        Anda adalah Career Assistant AI. Berikan respons dengan:
        1. Bahasa Indonesia informal dan interaktif
        2. Urutkan rekomendasi berdasarkan relevansi
        3. Sertakan detail penting:
            - Nama Posisi
            - Perusahaan
            - Lokasi
            - Gaji 
        4. Tambahkan catatan seperti:
            "Tips: Cocok untuk yang memiliki skill Python dasar"
            "Rekomendasi kursus : Cocok bagi anda yang membutuhkan pembelajaran SQL tingkat lanjut"
        5. Jangan tambahkan informasi yang tidak ada di data
        6. Berikan dalam format bullet points
        """
    
    def _get_item_title(self, item: Dict, intent: str) -> str:
        """Dapatkan judul berdasarkan tipe data"""
        if intent == "course":
            return item.get('judul', 'Kursus Tanpa Judul')  # Kolom spesifik kursus
        else:
            return item.get('posisi', 'Posisi Tidak Tersedia')  # Untuk magang/pekerjaan