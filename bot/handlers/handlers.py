from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import  NetworkError, TimedOut
import logging

# Fungsi Untuk Menjalankan Bot
async def start(update:Update, context:ContextTypes.DEFAULT_TYPE):
    text = '''
    🤖 Halo! Selamat datang di Virtual Assistant Bot!  

    Saya asisten digital yang siap membantu Anda mencari informasi tentang:  
    🔹 Lowongan magang  
    🔹 Peluang pekerjaan  
    🔹 Rekomendasi kursus/keterampilan  

    📢 **Penting untuk diketahui:**  
    Saya masih dalam tahap pengembangan aktif dan terus belajar. Saat ini saya memiliki beberapa keterbatasan:  
    - Jawaban mungkin belum sempurna (terutama dalam Bahasa Indonesia)  
    - Belum bisa memahami semua jenis pertanyaan  
    - Kadang merespon dengan kurang akurat  

    💪 Tim developer saat ini sedang bekerja keras untuk meningkatkan kemampuan saya setiap hari!  

    💡 Tips: Gunakan kalimat sederhana dan kata kunci jelas untuk hasil terbaik.  
'''
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

# Fungsi Help
async def help(update:Update, context:ContextTypes.DEFAULT_TYPE):
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

# Fungsi Info (Untuk Memahami Informasi tentang ChatBot)
async def info(update:Update, context: ContextTypes.DEFAULT_TYPE):
    info_text = (
        "🤖 Informasi Teknis:\n\n"
        "Model: Microsoft DialoGPT-small\n"
        "Arsitektur: GPT-2 kecil dengan 117M parameter\n"
        "Library: python-telegram-bot v20, Transformers, Torch\n\n"
        "Model ini dilatih terutama untuk bahasa Inggris, "
        "tetapi sudah dimodifikasi untuk memahami konteks bahasa Indonesia."
    )

    await context.bot.send_message(info_text)