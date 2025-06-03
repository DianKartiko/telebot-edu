from telegram import Update
from telegram.ext import ContextTypes

# Fungsi Untuk Menjalankan Bot
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