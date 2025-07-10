import re
from collections import Counter
from typing import List, Dict

class KeywordExtractor:
    def __init__(self):
        # Daftar kata kunci domain-spesifik
        self.domain_keywords = {
            "magang": ["magang", "internship", "pkl", "praktik kerja", "interns", "intern"],
            "pekerjaan": ["pekerjaan", "job", "lowongan", "karir", "rekrutmen", "loker"],
            "kursus": ["kursus", "pelatihan", "training", "bootcamp", "sertifikasi", "course", "program"],
            "bidang": ["data science", "marketing", "programmer", "design", "keuangan", "it", "bisnis" ],
            "lokasi": ["jakarta", "bandung", "surabaya", "remote", "hybrid", "online", "onsite", "tangerang", "banten", "freelance"]
        }
        
        # Precompile regex untuk efisiensi
        self.location_pattern = re.compile(r"\b(jakarta|bandung|surabaya|bali|remote)\b", flags=re.IGNORECASE)
        self.field_pattern = re.compile(r"\b(data science|digital marketing|web developer|ui/ux)\b", flags=re.IGNORECASE)

    def extract_keywords(self, text: str) -> Dict[str, List[str]]:
        """Ekstrak kata kunci terstruktur dari teks input"""
        text_lower = text.lower()
        
        # 1. Ekstraksi berbasis aturan (rule-based)
        rule_based_keywords = {
            "intent": self._detect_intent(text_lower),
            "bidang": self._extract_using_pattern(text_lower, self.field_pattern),
            "lokasi": self._extract_using_pattern(text_lower, self.location_pattern)
        }
        
        # 2. Ekstraksi statistik (tf-idf bisa digunakan di sini)
        statistical_keywords = self._extract_statistical(text_lower)
        
        # Gabungkan hasil
        return {
            **rule_based_keywords,
            "additional_keywords": statistical_keywords
        }

    def _detect_intent(self, text: str) -> str:
        """Deteksi intent utama menggunakan kata kunci"""
        for intent, keywords in self.domain_keywords.items():
            if any(keyword in text for keyword in keywords):
                return intent
        return "umum"

    def _extract_using_pattern(self, text: str, pattern) -> List[str]:
        """Ekstrak kata kunci menggunakan regex"""
        return list(set(pattern.findall(text)))

    def _extract_statistical(self, text: str, top_n: int = 3) -> List[str]:
        """Ekstrak kata penting berbasis frekuensi (sederhana)"""
        words = re.findall(r'\w+', text)
        word_counts = Counter(words)
        
        # Filter kata umum (stop words sederhana)
        stop_words = {"saya", "ini", "itu", "dan", "di"}
        meaningful_words = [
            word for word, count in word_counts.most_common() 
            if word not in stop_words and len(word) > 3
        ]
        
        return meaningful_words[:top_n]

