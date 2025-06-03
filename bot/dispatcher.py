from bot.handlers.start import start
from bot.handlers.help import help
from telegram.ext import CommandHandler, ApplicationBuilder, MessageHandler, filters
from bot.utils import logger
from bot.handlers.message_handler import handle_message, error_handler, start
from dotenv import load_dotenv
import os 

# Load Data
load_dotenv()

KEY = os.getenv('API_KEY')

# Logging 
log = logger.setup_logging()

def server():
    # Build Application Builder
    App = ApplicationBuilder().token(KEY).build()
    
    # Adding Command Handler 
    App.add_handler(CommandHandler('start', start.start))
    App.add_handler(CommandHandler('help', help.help))
    # Message Handler
    App.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    # Error Handler
    App.add_error_handler(error_handler)

    # Running Telebot
    print('Bot Is Running ...')
    App.run_polling()

