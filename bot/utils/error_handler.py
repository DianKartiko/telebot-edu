# bot/utils/error_handler.py
import logging
import os
import json
from typing import Optional
from huggingface_hub import login

class ErrorHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def handle_data_error(self, file_path: str) -> Optional[dict]:
        """Handle missing JSON data file"""
        try:
            if not os.path.exists(file_path):
                self._create_empty_data(file_path)
                return {}
            
            with open(file_path, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            self.logger.error(f"Data load error: {e}")
            return None
    
    def _create_empty_data(self, file_path: str):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump([], f)
    
    def handle_huggingface_error(self, repo_id: str, token: Optional[str] = None):
        """Handle HF model loading issues"""
        try:
            if token:
                login(token)
            
            if not repo_id or repo_id.lower() == 'none':
                raise ValueError("Invalid repo_id provided")
                
        except Exception as e:
            self.logger.error(f"HF auth error: {e}")
            return False
        return True