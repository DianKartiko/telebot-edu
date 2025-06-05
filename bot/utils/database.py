import sqlite3
from sqlite3 import Error
from typing import Optional, Dict, Tuple, List
from pathlib import Path
import logging

class DataBaseManager:
    def __init__(self, db_file:str='chat_history.db'):
        self.db_file=Path(db_file)
        self.logger = logging.getLogger(__name__)
        self._init_db()
    
    