import logging
from datetime import datetime
import os 
from dotenv import load_dotenv

load_dotenv()
LOG_FILE = os.getenv('LOG_FILE')

def setup_logging():    
    '''Configure Logging System'''
    # Loggin For Basic Configuration
    log = logging.basicConfig(
        filename=LOG_FILE,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)
    return log

def log_interaction(user_id:int, message:str, response:str, source:str):
    '''Log Interaction'''
    logging.info(
        f"User {user_id} - Message: {message[:50]}... | "
        f"Response: {response[:50]}... | Source: {source}"
    )


def get_current_time() -> str:
    '''Get Formatted Current Time'''
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")