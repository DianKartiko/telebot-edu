# main.py
from bot.dispatcher import Dispatcher
from bot.utils.logger import Logging

Logging.setup_logging()

# 3. Run server with fallback
if __name__ == "__main__":
    try:
        bot = Dispatcher()
        bot.run()
    except Exception as e:
        Logging.critical_error(e)
        # Implement restart mechanism here if needed