import logging

def logger():
        # Loggin For Basic Configuration
    log = logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
    return log
