from typing import Dict, List
from dotenv import load_dotenv
import os
from .data_processor import DataProcessor
from .dialogpt_manager import DialoGPTManager

load_dotenv()
CONFIDENCE_THRESHOLD = os.getenv('CONFIDENCE_THRESHOLD')

class ResponseGenerator:
    def __init__(self):
        self.data_processor = DataProcessor()
        self.dialogpt = DialoGPTManager()
        
    def generate_response(self, user_input: str, user_context: Dict = None) -> Dict:
        """
        Generate bot response with metadata
        Returns:
            {
                "text": str,
                "source": "database"|"dialogpt",
                "confidence": float,
                "data": List[Dict]|None
            }
        """
        # Try structured data first
        structured_response = self._generate_structured_response(user_input)
        
        if structured_response['confidence'] >= CONFIDENCE_THRESHOLD:
            return {
                "text": structured_response['text'],
                "source": "database",
                "confidence": structured_response['confidence'],
                "data": structured_response['data']
            }
        
        # Fallback to DialoGPT
        dialogpt_response = self.dialogpt.generate_response(user_input,context=self._get_dialogpt_context(user_context))
        
        return {
            "text": dialogpt_response or "Maaf, saya tidak mengerti pertanyaan Anda.",
            "source": "dialogpt",
            "confidence": 0.3,  # Low confidence for generative
            "data": None
        }
    
    def _generate_structured_response(self, user_input: str) -> Dict:
        """Generate response from structured data"""
        result = self.data_processor.find_matches(user_input)
        
        if not result['matches']:
            return {
                'text': '',
                'confidence': 0,
                'data': []
            }
        
        response_text = self._format_matches(result['matches'])
        return {
            'text': response_text,
            'confidence': result['confidence'],
            'data': [match['item'] for match in result['matches']]
        }
    
    def _format_matches(self, matches: List[Dict]) -> str:
        """Format matched items into natural language"""
        if not matches:
            return ""
        
        responses = []
        for match in matches:
            item = match['item']
            
            if item['type'] == 'magang':
                response = (
                    f"🏢 *{item['title']}*\n"
                    f"📍 {item.get('company', 'Perusahaan')} ({item.get('location', 'Lokasi')})\n"
                    f"📅 Periode: {item.get('period', '-')}\n"
                    f"📝 Syarat: {item.get('requirements', '-')}\n"
                )
            elif item['type'] == 'kursus':
                response = (
                    f"🎓 *{item['title']}*\n"
                    f"🌐 Platform: {item.get('platform', '-')}\n"
                    f"💵 Harga: {item.get('price', 'Gratis')}\n"
                    f"⏱ Durasi: {item.get('duration', '-')}\n"
                )
            
            if match.get('matched_keywords'):
                response += f"🔍 Cocok dengan: {', '.join(match['matched_keywords'])}\n"
            
            responses.append(response)
        
        header = "🔍 Saya menemukan beberapa rekomendasi:\n\n"
        return header + "\n\n".join(responses)
    
    def _get_dialogpt_context(self, user_context: Dict) -> str:
        """Create context string for DialoGPT"""
        if not user_context:
            return ""
        
        context_parts = []
        if user_context.get('major'):
            context_parts.append(f"User adalah mahasiswa {user_context['major']}")
        if user_context.get('location'):
            context_parts.append(f"berdomisili di {user_context['location']}")
        
        return ". ".join(context_parts) + ". " if context_parts else ""