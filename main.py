# main.py
from bot.dispatcher import Dispatcher
import logging
from bot.utils.logger import setup_logging

setup_logging()

# 3. Run server with fallback
if __name__ == "__main__":
    try:
        bot = Dispatcher()
        bot.run()
    except Exception as e:
        logging.critical(f"Fatal error: {str(e)}", exc_info=True)
        # Implement restart mechanism here if needed