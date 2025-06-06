from telegram.ext import CommandHandler, ApplicationBuilder, MessageHandler, filters
from bot.handlers.handlers import HandlerMessage
from bot.utils import logger
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import os 
from bot.scraper.interns import run_scraper
import logging

# Load Data
load_dotenv()
KEY = os.getenv("BOT_TOKEN")

logging = logging.getLogger(__name__)
log = logger.setup_logging()

class Dispatcher:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.handler = HandlerMessage()

    def run(self):
        """Jalankan bot dan scheduler"""
        # Scraping otomatis setiap 6 jam
        self.scheduler.add_job(
            run_scraper,
            "interval",
            hours=int(os.getenv("SCRAPER_INTERVAL"))
        )
        self.scheduler.start()

        # Build Application Builder
        app = ApplicationBuilder().token(KEY).build()
        
        # Adding Command Handler 
        app.add_handler(CommandHandler('start', self.handler.start))
        app.add_handler(CommandHandler('help', self.handler.help))
        app.add_handler(CommandHandler('info', self.handler.info))

        # adding Message Handler
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handler.handler_message))
        
        # Error Handling dalam pesan
        app.add_error_handler(self.handler.error_handler)


        # Running Telebot
        logging.info("🤖 Bot berjalan...")
        app.run_polling()

