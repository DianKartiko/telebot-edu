import os
import re
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from dotenv import load_dotenv
import requests
from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.database import DatabaseJob, DatabaseCourse, DatabaseIntern
from bot.utils.keywords_extraction import KeywordExtractor
import logging

load_dotenv()

class IntentType(Enum):
    MAGANG = "magang"
    PEKERJAAN = "pekerjaan"
    KURSUS = "kursus"
    GREETING = "greeting"
    UNKNOWN = "unknown"

@dataclass
class UserContext:
    user_id: int
    conversation_history: List[Dict]
    last_search_type: Optional[str] = None
    preferences: Dict = None
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {}

class ConversationManager:
    """Mengelola konteks percakapan untuk setiap user"""
    
    def __init__(self):
        self.user_contexts: Dict[int, UserContext] = {}
        self.MAX_HISTORY = 5  # Batasi riwayat untuk efisiensi
    
    def get_context(self, user_id: int) -> UserContext:
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = UserContext(
                user_id=user_id,
                conversation_history=[]
            )
        return self.user_contexts[user_id]
    
    def add_message(self, user_id: int, role: str, content: str):
        context = self.get_context(user_id)
        context.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Batasi riwayat
        if len(context.conversation_history) > self.MAX_HISTORY * 2:
            context.conversation_history = context.conversation_history[-self.MAX_HISTORY * 2:]

class EnhancedIntentDetector:
    """Deteksi intent yang lebih akurat dengan pattern matching"""
    
    def __init__(self):
        self.patterns = {
            IntentType.MAGANG: [
                r'\b(magang|internship|intern|praktek kerja|pkl)\b',
                r'\bcari.*magang\b',
                r'\bintern.*program\b'
            ],
            IntentType.PEKERJAAN: [
                r'\b(kerja|job|pekerjaan|lowongan|karir)\b',
                r'\bcari.*kerja\b',
                r'\blowongan.*kerja\b',
                r'\bfull.*time\b'
            ],
            IntentType.KURSUS: [
                r'\b(kursus|course|pelatihan|training|belajar)\b',
                r'\bcari.*kursus\b',
                r'\bingin.*belajar\b'
            ],
            IntentType.GREETING: [
                r'\b(hai|halo|hello|hi|selamat)\b',
                r'\bapa kabar\b',
                r'\bmulai\b'
            ],
        }
    
    def detect_intent(self, text: str) -> IntentType:
        text_lower = text.lower()
        
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return intent
        
        return IntentType.UNKNOWN

class EnhancedLLMIntegration:
    """Enhanced LLM Integration dengan UX yang lebih baik"""
    
    def __init__(self):
        self.HF_TOKEN = os.getenv('HF_TOKEN')
        self.API_URL = os.getenv('API_URL')
        self.HEADERS = {
            "Authorization": f"Bearer {self.HF_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Database instances
        self.db_job = DatabaseJob()
        self.db_course = DatabaseCourse()
        self.db_intern = DatabaseIntern()
        self.extractor = KeywordExtractor()
        
        # Enhanced components
        self.intent_detector = EnhancedIntentDetector()
        self.conversation_manager = ConversationManager()
        
        # Response templates
        self.response_templates = {
            IntentType.GREETING: self._get_greeting_response,
            IntentType.UNKNOWN: self._get_unknown_response
        }
    
    async def process_user_request(self, user_input: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Proses request dengan context awareness dan intent detection"""
        try:
            user_id = update.effective_user.id
            user_context = self.conversation_manager.get_context(user_id)
            
            # Deteksi intent
            intent = self.intent_detector.detect_intent(user_input)
            
            # Handle special intents
            if intent in self.response_templates:
                response = await self.response_templates[intent](user_input, user_context)
                self.conversation_manager.add_message(user_id, "user", user_input)
                self.conversation_manager.add_message(user_id, "assistant", response)
                return response
            
            # Handle search intents
            if intent in [IntentType.MAGANG, IntentType.PEKERJAAN, IntentType.KURSUS]:
                return await self._handle_search_intent(user_input, intent, update, context, user_context)
            
            # Fallback untuk intent unknown
            return await self._handle_unknown_with_search(user_input, update, context, user_context)
            
        except Exception as e:
            logging.error(f"Error in process_user_request: {str(e)}")
            return f"⚠️ Terjadi error: {str(e)[:100]}..."
    
    async def _handle_search_intent(self, user_input: str, intent: IntentType, 
                                    update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                    user_context: UserContext) -> str:
        """Handle search dengan context awareness"""
        
        # Extract keywords
        keywords = self.extractor.extract(user_input)
        
        # Search database
        items = await self._search_database(intent, keywords)
        
        if not items:
            return await self._handle_empty_results(intent, keywords, update, context, user_context)
        
        # Update context
        user_context.last_search_type = intent.value
        
        # Generate enhanced response
        prompt = self._build_enhanced_prompt(user_input, intent, keywords, items, user_context)
        response = await self.generate_response(
            messages=[{"role": "user", "content": prompt}],
            update=update,
            context=context
        )
        
        # Save to context
        user_id = update.effective_user.id
        self.conversation_manager.add_message(user_id, "user", user_input)
        self.conversation_manager.add_message(user_id, "assistant", response)
        
        return response
    
    async def _search_database(self, intent: IntentType, keywords: Dict) -> List[Dict]:
        """Search database berdasarkan intent"""
        items = []
        
        try:
            if intent == IntentType.MAGANG:
                items = self.db_intern.search_magang(
                    keyword=" ".join(keywords.get("field", [])),
                    location=" ".join(keywords.get("location", [])),
                    limit=8
                )
            elif intent == IntentType.PEKERJAAN:
                items = self.db_job.search_jobs(
                    keyword=" ".join(keywords.get("field", [])),
                    location=" ".join(keywords.get("location", [])),
                    limit=8
                )
            elif intent == IntentType.KURSUS:
                items = self.db_course.search_course(
                    keyword=" ".join(keywords.get("field", [])),
                    limit=8
                )
        except Exception as e:
            logging.error(f"Error searching database: {str(e)}")
            items = []
        
        return items
    
    def _build_enhanced_prompt(self, user_input: str, intent: IntentType, 
                                keywords: Dict, items: List[Dict], 
                                context: UserContext) -> str:
        """Build prompt yang lebih interactive dan contextual"""
        
        # Format items berdasarkan intent
        items_str = self._format_items_for_prompt(items, intent)
        
        # Build context dari conversation history
        context_str = self._build_context_string(context)
        
        # Personality dan tone
        personality = self._get_personality_prompt()
        
        prompt = f"""
{personality}

KONTEKS PERCAKAPAN:
{context_str}

PERMINTAAN USER: "{user_input}"
INTENT: {intent.value}
KEYWORDS: {keywords}

DATA HASIL PENCARIAN:
{items_str}

INSTRUKSI RESPONS:
1. WAJIB menggunakan bahasa Indonesia yang ramah, natural, dan interaktif namun informal
2. Berikan rekomendasi dalam format yang mudah dibaca
3. Sertakan detail penting: posisi, perusahaan, lokasi, gaji (jika ada)
4. Tambahkan tips atau insight yang berguna
5. PENTING: Akhiri dengan pertanyaan follow-up yang relevan untuk memicu interaksi
6. Gunakan emoji yang sesuai untuk membuat respons lebih menarik
7. Jika data terbatas, berikan saran sesuai dengan data 

CONTOH AKHIRAN INTERAKTIF:
- "Apakah ada bidang spesifik yang lebih kamu minati?"
- "Mau saya carikan info gaji untuk posisi ini?"
- "Butuh rekomendasi kursus untuk persiapan interview?"
- PENTING: Jika terdapat data yang terbatas akhiri dengan:
- "Yah, data yang tersedia terbatas dan hanya itu yang sesuai"
- "Maaf ya, data yang dicari terbatas"
- "Saya bisa merekomendasikan pekerjaan yang lain jika tidak keberatan"

FORMAT RESPONS:
- Gunakan bullet points untuk daftar dan font bold untuk judul
- Berikan ranking berdasarkan relevansi
- Sertakan call-to-action yang jelas
"""
        
        return prompt
    
    def _format_items_for_prompt(self, items: List[Dict], intent: IntentType) -> str:
        """Format items sesuai dengan intent"""
        if not items:
            return "Tidak ada data yang ditemukan."
        
        formatted_items = []
        
        for idx, item in enumerate(items[:6], 1):  # Limit to 6 items
            if intent == IntentType.KURSUS:
                formatted_items.append(
                    f"{idx}. {item.get('title', 'Judul tidak tersedia')}\n"
                    f"   Platform: {item.get('sumber', 'N/A')}\n"
                    f"   Durasi: {item.get('duration', 'N/A')}\n"
                    f"   Modul: {item.get('module_total', 'N/A')}"
                )
            else:
                formatted_items.append(
                    f"{idx}. {item.get('posisi', 'Posisi tidak tersedia')}\n"
                    f"   Perusahaan: {item.get('perusahaan', 'N/A')}\n"
                    f"   Lokasi: {item.get('lokasi', 'N/A')}\n"
                    f"   Gaji: {item.get('gaji', 'Tidak disebutkan')}\n"
                    f"   Deadline: {item.get('deadline', 'N/A')}"
                )
        
        return "\n\n".join(formatted_items)
    
    def _build_context_string(self, context: UserContext) -> str:
        """Build context string dari conversation history"""
        if not context.conversation_history:
            return "Ini adalah percakapan pertama dengan user."
        
        recent_messages = context.conversation_history[-4:]  # Last 4 messages
        context_parts = []
        
        for msg in recent_messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts)
    
    def _get_personality_prompt(self) -> str:
        """Define AI personality"""
        return """
IDENTITAS: Kamu adalah CareerBot, asisten AI yang ramah dan membantu untuk mencari magang, pekerjaan, dan kursus.

KEPRIBADIAN:
- Ramah dan supportive
- Memberikan saran yang praktis
- Selalu optimis dan encouraging
- Responsif terhadap kebutuhan user
- Menggunakan bahasa yang natural dan tidak kaku

TUJUAN: Membantu user menemukan peluang karir yang sesuai dengan kebutuhan mereka.
"""
    
    async def _handle_empty_results(self, intent: IntentType, keywords: Dict, 
                                    update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                    user_context: UserContext) -> str:
        """Handle ketika tidak ada hasil pencarian"""
        
        suggestions = {
            IntentType.MAGANG: [
                "Coba gunakan kata kunci yang lebih umum seperti 'IT', 'Marketing', 'Finance'",
                "Periksa ejaan kata kunci yang digunakan",
                "Coba tanpa menyebutkan lokasi spesifik"
            ],
            IntentType.PEKERJAAN: [
                "Gunakan kata kunci posisi yang lebih umum",
                "Coba cari berdasarkan industri seperti 'teknologi', 'perbankan'",
                "Periksa apakah lokasi yang dicari tersedia"
            ],
            IntentType.KURSUS: [
                "Coba kata kunci yang lebih spesifik seperti 'Python', 'Digital Marketing'",
                "Gunakan bahasa Indonesia atau Inggris",
                "Cari berdasarkan kategori seperti 'programming', 'design'"
            ]
        }
        
        intent_name = {
            IntentType.MAGANG: "magang",
            IntentType.PEKERJAAN: "pekerjaan", 
            IntentType.KURSUS: "kursus"
        }
        
        suggestion_list = suggestions.get(intent, [])
        suggestion_text = "\n".join([f"• {s}" for s in suggestion_list])
        
        return f"""
🔍 Maaf, tidak menemukan hasil untuk pencarian {intent_name.get(intent, 'tersebut')}.

💡 **Saran pencarian:**
{suggestion_text}

🤔 **Atau coba tanyakan:**
- "Tampilkan semua magang di bidang IT"
- "Cari pekerjaan remote"
- "Kursus programming untuk pemula"

Mau coba dengan kata kunci yang berbeda? Saya siap membantu! 😊
"""
    
    async def _get_greeting_response(self, user_input: str, context: UserContext) -> str:
        """Response untuk greeting"""
        return """
👋 Halo! Saya CareerBot, asisten AI yang siap membantu kamu mencari:

🎯 **Magang (Internship)**
💼 **Pekerjaan (Jobs)**  
📚 **Kursus (Courses)**

✨ **Contoh yang bisa kamu tanyakan:**
• "Cari magang di bidang IT"
• "Pekerjaan remote developer"
• "Kursus digital marketing"

Apa yang sedang kamu cari hari ini? 😊
"""
    
    async def _get_unknown_response(self, user_input: str, context: UserContext) -> str:
        """Response untuk intent yang tidak dikenali"""
        return """
🤔 Maaf, saya tidak yakin apa yang kamu maksud.

Saya bisa membantu kamu mencari:
• 🎯 **Magang** - ketik "cari magang [bidang]"
• 💼 **Pekerjaan** - ketik "cari kerja [posisi]"
• 📚 **Kursus** - ketik "cari kursus [topik]"

Atau ketik "/help" untuk panduan lengkap.

Coba tanyakan dengan cara yang lebih spesifik ya! 😊
"""
    
    async def _handle_unknown_with_search(self, user_input: str, update: Update, 
                                            context: ContextTypes.DEFAULT_TYPE,
                                            user_context: UserContext) -> str:
        """Handle unknown intent dengan mencoba search"""
        
        # Coba ekstrak keywords dan search
        keywords = self.extractor.extract(user_input)
        
        # Search di semua database
        all_items = []
        
        try:
            # Search magang
            magang_items = self.db_intern.search_magang(
                keyword=" ".join(keywords.get("field", [])),
                location=" ".join(keywords.get("location", [])),
                limit=3
            )
            all_items.extend([{**item, "type": "magang"} for item in magang_items])
            
            # Search jobs
            job_items = self.db_job.search_jobs(
                keyword=" ".join(keywords.get("field", [])),
                location=" ".join(keywords.get("location", [])),
                limit=3
            )
            all_items.extend([{**item, "type": "pekerjaan"} for item in job_items])
            
            # Search courses
            course_items = self.db_course.search_course(
                keyword=" ".join(keywords.get("field", [])),
                limit=3
            )
            all_items.extend([{**item, "type": "kursus"} for item in course_items])
            
        except Exception as e:
            logging.error(f"Error in unknown search: {str(e)}")
            all_items = []
        
        if all_items:
            prompt = f"""
Kamu adalah CareerBot yang ramah. User menanyakan: "{user_input}"

Saya menemukan beberapa hasil yang mungkin relevan:

{self._format_mixed_items(all_items)}

Berikan respons yang:
1. Mengakui bahwa pertanyaan agak ambigu
2. Tunjukkan hasil yang ditemukan
3. Tanyakan klarifikasi untuk membantu lebih baik
4. Gunakan tone yang ramah dan helpful
5. Akhiri dengan pertanyaan yang memicu interaksi

Gunakan emoji dan format yang menarik.
"""
            
            return await self.generate_response(
                messages=[{"role": "user", "content": prompt}],
                update=update,
                context=context
            )
        
        return await self._get_unknown_response(user_input, user_context)
    
    def _format_mixed_items(self, items: List[Dict]) -> str:
        """Format mixed items dari berbagai tipe"""
        formatted = []
        
        for item in items:
            item_type = item.get("type", "")
            if item_type == "kursus":
                formatted.append(
                    f"📚 {item.get('title', 'N/A')} - {item.get('sumber', 'N/A')}"
                )
            else:
                formatted.append(
                    f"{'🎯' if item_type == 'magang' else '💼'} {item.get('posisi', 'N/A')} - {item.get('perusahaan', 'N/A')}"
                )
        
        return "\n".join(formatted)
    
    async def generate_response(self, messages: List[dict], update: Update, 
                               context: ContextTypes.DEFAULT_TYPE) -> str:
        """Generate response dengan error handling yang lebih baik"""
        payload = {
            "messages": messages,
            "model": "SeaLLMs/SeaLLMs-v3-7B-Chat",
            "stream": True,
            "max_tokens": 800,
            "temperature": 0.7,
            "top_p": 0.9
        }

        full_response = ""
        
        try:
            # Set timeout untuk request
            timeout = 30
            
            response = requests.post(
                self.API_URL, 
                headers=self.HEADERS, 
                json=payload, 
                stream=True, 
                timeout=timeout
            )
            response.raise_for_status()
            
            has_content = False
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8').strip()
                    if decoded_line.startswith("data:"):
                        try:
                            chunk = json.loads(decoded_line[5:])
                            if chunk.get("choices"):
                                content = chunk["choices"][0]["delta"].get("content", "")
                                if content:
                                    has_content = True
                                    full_response += content
                        except json.JSONDecodeError:
                            continue

            # Handle empty response
            if not has_content or not full_response.strip():
                full_response = "⚠️ Maaf, tidak dapat memberikan respons saat ini. Coba lagi dalam beberapa saat."
            
            return full_response.strip()

        except requests.exceptions.Timeout:
            return "⏱️ Respons terlalu lama. Coba lagi dengan pertanyaan yang lebih sederhana."
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error: {str(e)}")
            return "🚨 Terjadi masalah koneksi. Silakan coba lagi."
        except Exception as e:
            logging.error(f"Unexpected error in generate_response: {str(e)}")
            return f"🚨 Terjadi error: {str(e)[:100]}..."