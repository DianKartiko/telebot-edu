from bot.handlers.handlers import start, help, info
from bot.handlers.error_handlers import error_handler
from telegram.ext import CommandHandler, ApplicationBuilder, MessageHandler, filters
from bot.utils import logger
from dotenv import load_dotenv
import os 

# Load Data
load_dotenv()

KEY = os.getenv('API_KEY')

# Logging 
log = logger.setup_logging()

def server():
    # Build Application Builder
    app = ApplicationBuilder().token(KEY).build()
    
    # Adding Command Handler 
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help))
    app.add_handler(CommandHandler('info', info))
    
    # Error Handling dalam pesan
    app.add_error_handler(error_handler)


    # Running Telebot
    print('Bot Is Running ...')
    app.run_polling()

