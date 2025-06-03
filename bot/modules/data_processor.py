import json
import re
from fuzzywuzzy import fuzz
from typing import Dict, List
from dotenv import load_dotenv
import os

load_dotenv()
DATA_JSON_PATH = os.getenv("DATA_JSON_PATH")
MAX_RECOMMENDATIONS = os.getenv("MAX_RECOMMENDATIONS")

class DataProcessor:
    def __init__(self):
        self.data = self._load_with_fallback()
    
    def _load_with_fallback(self) -> List[Dict]:
        """Multi-layer fallback loading"""
        try:
            # Try primary path
            with open(DATA_JSON_PATH) as f:
                return json.load(f)
        except FileNotFoundError:
            # Try backup path
            try:
                with open('database/backup_data.json') as f:
                    return json.load(f)
            except:
                # Return minimal dataset
                return [
                    {
                        "type": "magang",
                        "title": "Contoh Magang",
                        "company": "Perusahaan Contoh",
                        "location": "Jakarta",
                        "requirements": "Minimal semester 5"
                    }
                ]
    
    def preprocess_text(self, text: str) -> str:
        """Normalize user input text"""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)
        return text
    
    def find_matches(self, user_input: str) -> Dict:
        """Find matches in JSON data with confidence score"""
        processed_input = self.preprocess_text(user_input)
        matched_items = []
        
        for item in self.data:
            score = 0
            
            # Type matching
            if item.get('type'):
                type_words = [item['type']] + item.get('type_synonyms', [])
                if any(word in processed_input for word in type_words):
                    score += 30
            
            # Keyword matching
            for keyword in item.get('keywords', []):
                if fuzz.partial_ratio(keyword, processed_input) > 70:
                    score += 15
            
            # Location matching
            if 'location' in item and item['location'].lower() in processed_input:
                score += 20
            
            if score > 0:
                matched_items.append({
                    'item': item,
                    'score': score,
                    'matched_keywords': self._get_matched_keywords(processed_input, item)
                })
        
        # Sort by score and take top matches
        matched_items.sort(key=lambda x: x['score'], reverse=True)
        return {
            'matches': matched_items[:MAX_RECOMMENDATIONS],
            'confidence': min(100, sum(m['score'] for m in matched_items)) / 100
        }
    
    def _get_matched_keywords(self, text: str, item: Dict) -> List[str]:
        """Extract which keywords triggered the match"""
        matched = []
        for keyword in item.get('keywords', []):
            if keyword in text or fuzz.partial_ratio(keyword, text) > 70:
                matched.append(keyword)
        return matched