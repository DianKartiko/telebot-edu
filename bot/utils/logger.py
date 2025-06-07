import logging
from datetime import datetime
import os 
from dotenv import load_dotenv

load_dotenv()

class Logging:
    def setup_logging():    
        '''Configure Logging System'''
        # Loggin For Basic Configuration
        return logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO)
        

    def log_interaction( user_id:int, message:str, response:str, source:str):
        '''Log Interaction'''
        return logging.info(
            f"User {user_id} - Message: {message[:50]}... | "
            f"Response: {response[:50]}... | Source: {source}"
        )
        


    def get_current_time() -> str:
        '''Get Formatted Current Time'''
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def critical_error(x):
        return logging.critical(
            f"Fatal error: {str(x)}", exc_info=True
        )

        

