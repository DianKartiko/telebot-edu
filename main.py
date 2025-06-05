# main.py
from bot.dispatcher import server
from bot.utils.logger import setup_logging
from dotenv import load_dotenv
import os
import logging

setup_logging()

# 3. Run server with fallback
if __name__ == "__main__":
    try:
        server()
    except Exception as e:
        logging.critical(f"Server crash: {e}")
        # Implement restart mechanism here if needed