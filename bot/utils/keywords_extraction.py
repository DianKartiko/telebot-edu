from typing import List, Dict

class KeywordExtractor:
    """Ekstrak kata kunci dari input pengguna"""
    @staticmethod
    def extract(text: str) -> Dict:
        text = text.lower()
        return {
            "intent": KeywordExtractor._detect_intent(text),
            "field": KeywordExtractor._extract_field(text),
            "location": KeywordExtractor._extract_location(text)
        }

    @staticmethod
    def _detect_intent(text: str) -> str:
        if any(k in text for k in ["magang", "internship", "pkl", "praktik kerja"]):
            return "magang"
        elif any(k in text for k in ["pekerjaan", "job", "lowongan", "karir", "rekrutmen", "loker"]):
            return "pekerjaan"
        elif any(k in text for k in ["kursus", "pelatihan", "training", "bootcamp", "sertifikasi"]):
            return "kursus"
        return "umum"

    @staticmethod
    def _extract_field(text: str) -> List[str]:
        fields = ["data science", "marketing", "programmer","design", "keuangan", "bisnis", "it"]
        return [f for f in fields if f in text]

    @staticmethod
    def _extract_location(text: str) -> List[str]:
        locations = ["jakarta", "bandung", "remote", "hybrid", "online", "onsite", "tangerang", "banten", "semarang", "yogyakarta"]
        return [loc for loc in locations if loc in text]

