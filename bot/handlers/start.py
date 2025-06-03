from telegram import Update
from telegram.ext import ContextTypes

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