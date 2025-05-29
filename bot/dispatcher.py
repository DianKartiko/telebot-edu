from bot.handlers import start
from telegram.ext import CommandHandler, ApplicationBuilder
from bot.utils import logger
from dotenv import load_dotenv
import os 

# Load Data
load_dotenv()

KEY = os.getenv('API_KEY')

# Logging 
log = logger.logger()

def server():
    # Build Application Builder
    App = ApplicationBuilder().token(KEY).build()
    
    # Adding Command Handler 
    App.add_handler(CommandHandler('start', start.start))

    # Running Telebot
    App.run_polling()

