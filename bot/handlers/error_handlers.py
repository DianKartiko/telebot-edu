from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import  NetworkError, TimedOut
import logging

async def error_handler(update:Update, context: ContextTypes.DEFAULT_TYPE):
    '''Menangani Error Handling yang terjadi di Bot'''
    logging.error('Exception while handling an update:', exc_info=context.error)

    if not update and not hasattr(update, 'effective_message'):
        return
    
    error = context.error
    user_message = "Maaf, Terjadi Kesalahan"

    if isinstance(error, NetworkError):
        user_message = "masalah koneksi. tolong coba lagi nanti".title()
    elif isinstance(error, TimedOut):
        user_message = "waktu respon habis. mohon coba lagi".title()
    elif isinstance(error, ValueError):
        user_message = "input tidak valid. silahkan coba input yang berbeda".title()
    elif isinstance(error, IndexError):
        user_message = "terjadi kesalahan dalam pemrosesan data".title()

    try:
        await update.effective_message.reply_text(
            f"{user_message}\n\n"
            "Gunakan /help untuk bantuan dan /start untuk memulai kembali"
        )
    except Exception as e:
        logging.error('Gagal mengirim pesan error: 'exc_info=e)