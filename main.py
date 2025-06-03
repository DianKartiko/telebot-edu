# main.py
from bot.dispatcher import server
from bot.utils.error_handler import ErrorHandler
from dotenv import load_dotenv
import os
import logging

# Initialize
load_dotenv()
error_handler = ErrorHandler()

# 1. Handle missing data file
DATA_PATH = 'database/interns_data.json'
if not error_handler.handle_data_error(DATA_PATH):
    logging.warning("Using empty dataset as fallback")

# 2. Handle HuggingFace auth
HF_TOKEN = os.getenv('HF_TOKEN')
HF_REPO = os.getenv('HF_REPO', 'microsoft/DialoGPT-medium')

if not error_handler.handle_huggingface_error(HF_REPO, HF_TOKEN):
    logging.warning("DialoGPT disabled, using rule-based only")
    os.environ['DIALOGPT_ENABLED'] = 'False'

# 3. Run server with fallback
if __name__ == "__main__":
    try:
        server()
    except Exception as e:
        logging.critical(f"Server crash: {e}")
        # Implement restart mechanism here if needed