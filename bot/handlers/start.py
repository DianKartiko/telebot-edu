import logging
from telegram import Update
from telegram.ext import ContextTypes

# Fungsi Untuk Menjalankan Bot
async def start(update:Update, context:ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome!!!")