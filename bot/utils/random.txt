import re
from typing import Dict, List, Set
from dataclasses import dataclass

@dataclass
class KeywordExtractionResult:
    intent: str
    field: List[str]
    location: List[str]
    experience_level: List[str]
    work_type: List[str]
    confidence: float

class EnhancedKeywordExtractor:
    """Enhanced keyword extraction dengan NLP sederhana"""
    
    def __init__(self):
        # Pola untuk bidang/field
        self.field_patterns = {
            'IT': [
                r'\b(programmer|developer|software|IT|teknologi|web|mobile|frontend|backend|fullstack|devops|data scientist|machine learning|AI|cyber security|database|network|sistem|analyst|tester|QA|UI|UX|cloud|programming|coding|java|python|javascript|react|angular|vue|node|laravel|spring|flutter|android|ios|kotlin|swift|golang|rust|scala|php|ruby|dotnet|c\+\+|c#)\b',
                r'\b(web.*dev|mobile.*dev|full.*stack|data.*science|machine.*learning|cyber.*security|software.*engineer|system.*admin|network.*engineer|database.*admin|cloud.*engineer|devops.*engineer|security.*engineer|ai.*engineer|ml.*engineer|qa.*engineer|backend.*dev|frontend.*dev|fullstack.*dev)\b'
            ],
            'Marketing': [
                r'\b(marketing|digital marketing|social media|content|brand|campaign|advertising|promotion|public relations|pr|seo|sem|ppc|email marketing|influencer|copywriter|content creator|growth hacker|brand manager|product marketing|affiliate|crm|lead generation)\b',
                r'\b(digital.*marketing|social.*media|content.*marketing|brand.*marketing|email.*marketing|performance.*marketing|growth.*marketing|product.*marketing|affiliate.*marketing|influencer.*marketing)\b'
            ],
            'Finance': [
                r'\b(finance|accounting|audit|tax|treasury|investment|banking|financial|analyst|controller|bookkeeper|payroll|budget|risk management|compliance|credit|loan|insurance|wealth management|portfolio|trading|forex|crypto|fintech)\b',
                r'\b(financial.*analyst|risk.*analyst|investment.*analyst|credit.*analyst|budget.*analyst|financial.*controller|audit.*manager|tax.*consultant|treasury.*analyst|wealth.*manager|portfolio.*manager|compliance.*officer|loan.*officer|insurance.*agent|trading.*analyst)\b'
            ],
            'Human Resources': [
                r'\b(hr|human resources|recruitment|recruiter|talent acquisition|people ops|organizational development|training|learning|compensation|benefits|payroll|employee relations|performance management|hris|talent management|workforce planning|culture|engagement)\b',
                r'\b(human.*resources|talent.*acquisition|people.*operations|organizational.*development|employee.*relations|performance.*management|talent.*management|workforce.*planning|compensation.*benefits|learning.*development|culture.*engagement)\b'
            ],
            'Sales': [
                r'\b(sales|business development|account manager|customer success|relationship manager|sales representative|sales executive|business analyst|crm|lead generation|prospecting|closing|negotiation|retail|wholesale|channel|partnership|revenue|quota|pipeline)\b',
                r'\b(business.*development|account.*manager|customer.*success|relationship.*manager|sales.*representative|sales.*executive|sales.*manager|business.*analyst|customer.*service|sales.*support|channel.*manager|partnership.*manager|revenue.*manager)\b'
            ],
            'Operations': [
                r'\b(operations|logistics|supply chain|procurement|purchasing|inventory|warehouse|shipping|distribution|quality control|quality assurance|production|manufacturing|lean|six sigma|process improvement|project management|operational excellence)\b',
                r'\b(supply.*chain|quality.*control|quality.*assurance|process.*improvement|project.*management|operational.*excellence|inventory.*management|warehouse.*management|logistics.*coordinator|procurement.*specialist|production.*manager|manufacturing.*engineer)\b'
            ],
            'Design': [
                r'\b(design|designer|creative|art|graphic|visual|ui|ux|product design|web design|brand design|logo|illustration|animation|video|photography|adobe|figma|sketch|photoshop|illustrator|indesign|after effects|premiere|cinema 4d|blender|maya|3d|motion graphics)\b',
                r'\b(graphic.*design|visual.*design|product.*design|web.*design|brand.*design|motion.*graphics|user.*interface|user.*experience|creative.*director|art.*director|visual.*artist|multimedia.*designer|game.*designer|interior.*design|fashion.*design)\b'
            ],
            'Engineering': [
                r'\b(engineer|engineering|mechanical|electrical|civil|chemical|industrial|manufacturing|automotive|aerospace|biomedical|environmental|structural|materials|petroleum|mining|nuclear|robotics|automation|cad|plc|scada|matlab|solidworks|autocad)\b',
                r'\b(mechanical.*engineer|electrical.*engineer|civil.*engineer|chemical.*engineer|industrial.*engineer|manufacturing.*engineer|automotive.*engineer|aerospace.*engineer|biomedical.*engineer|environmental.*engineer|structural.*engineer|materials.*engineer|petroleum.*engineer|mining.*engineer|nuclear.*engineer|robotics.*engineer|automation.*engineer)\b'
            ],
            'Healthcare': [
                r'\b(healthcare|medical|nurse|doctor|physician|pharmacist|therapist|medical assistant|healthcare assistant|medical technician|laboratory|radiology|pharmacy|clinical|hospital|clinic|patient care|medical device|pharmaceutical|biotech|health|wellness)\b',
                r'\b(medical.*assistant|healthcare.*assistant|medical.*technician|laboratory.*technician|radiology.*technician|pharmacy.*technician|clinical.*research|patient.*care|medical.*device|pharmaceutical.*research|health.*care|wellness.*coordinator)\b'
            ],
            'Education': [
                r'\b(education|teacher|instructor|tutor|trainer|academic|curriculum|e-learning|educational technology|student services|administration|principal|dean|professor|lecturer|research|library|campus|school|university|college|training|learning)\b',
                r'\b(educational.*technology|student.*services|curriculum.*development|academic.*advisor|research.*assistant|library.*assistant|campus.*administrator|school.*administrator|university.*administrator|college.*administrator|training.*coordinator|learning.*coordinator)\b'
            ]
        }
        
        # Pola untuk lokasi
        self.location_patterns = {
            'Jakarta': [r'\b(jakarta|jkt|dki|ibu kota|ibukota|kemang|menteng|sudirman|thamrin|kuningan|senayan|kelapa gading|pondok indah|kebayoran|tanah abang|gambir|sawah besar|senen|cempaka putih|johar baru|kemayoran|grogol petamburan|tambora|taman sari|cengkareng|kembangan|kebon jeruk|palmerah|kota administrasi|jakarta pusat|jakarta utara|jakarta selatan|jakarta timur|jakarta barat)\b'],
            'Bandung': [r'\b(bandung|bdg|kota kembang|paris van java|dago|cihampelas|braga|asia afrika|gasibu|alun-alun|cicendo|coblong|sukasari|sukajadi|cidadap|andir|astanaanyar|babakan ciparay|batununggal|bojongloa kaler|bojongloa kidul|buahbatu|cibeunying kaler|cibeunying kidul|cibiru|gedebage|kiaracondong|lengkong|mandalajati|panyileukan|rancasari|regol|ujung berung|arcamanik|antapani|bandung kidul|bandung kulon|bandung wetan|cinambo|margacinta|margahayu|ujung berung)\b'],
            'Surabaya': [r'\b(surabaya|sby|kota pahlawan|hero city|tunjungan|gubeng|wonokromo|sawahan|genteng|bubutan|simokerto|pabean cantian|krembangan|semampir|bulak|kenjeran|lakarsantri|benowo|pakal|asemrowo|sukomanunggal|tandes|sambikerep|dukuh pakis|gayungan|jambangan|karang pilang|wonocolo|wiyung|mulyorejo|gunung anyar|rungkut|tenggilis mejoyo|sukolilo)\b'],
            'Medan': [r'\b(medan|mdn|kota medan|medan kota|medan timur|medan barat|medan utara|medan selatan|medan tembung|medan amplas|medan area|medan baru|medan belawan|medan deli|medan denai|medan helvetia|medan johor|medan krio|medan labuhan|medan maimun|medan marelan|medan petisah|medan polonia|medan selayang|medan sunggal|medan tuntungan)\b'],
            'Yogyakarta': [r'\b(yogyakarta|yogya|jogja|jogjakarta|diy|istimewa|gudeg|malioboro|tugu|kraton|pakualaman|kotagede|umbulharjo|mergangsan|danurejan|gedongtengen|ngampilan|wirobrajan|mantrijeron|gondomanan|jetis|tegalrejo|umbulharjo)\b'],
            'Semarang': [r'\b(semarang|smg|kota semarang|semarang tengah|semarang utara|semarang selatan|semarang timur|semarang barat|candisari|gajahmungkur|gayamsari|genuk|gunungpati|mijen|ngaliyan|pedurungan|tembalang|tugu|banyumanik)\b'],
            'Makassar': [r'\b(makassar|ujung pandang|kota makassar|mariso|mamajang|tamalate|rappocini|makassar|ujung tanah|tallo|bontoala|ujung pandang|wajo|kepulauan sangkarrang|biringkanaya|tamalanrea|manggala|pangkajene)\b'],
            'Palembang': [r'\b(palembang|plg|kota palembang|ilir barat|ilir timur|seberang ulu|kemuning|kalidoni|bukit kecil|gandus|kertapati|plaju|radial|sako|sematang borang|sukarami|alang-alang lebar|jakabaring)\b'],
            'Bali': [r'\b(bali|denpasar|ubud|sanur|kuta|seminyak|nusa dua|jimbaran|uluwatu|canggu|tabanan|gianyar|bangli|klungkung|karangasem|buleleng|badung|denpasar utara|denpasar selatan|denpasar timur|denpasar barat)\b'],
            'Batam': [r'\b(batam|kota batam|nagoya|sekupang|sagulung|batu aji|nongsa|lubuk baja|sei beduk|bulang|galang|riau kepulauan|kepri)\b'],
            'Balikpapan': [r'\b(balikpapan|bpp|kota balikpapan|balikpapan utara|balikpapan selatan|balikpapan timur|balikpapan barat|balikpapan tengah|sepinggan|kariangau|manggar|klandasan)\b'],
            'Remote': [r'\b(remote|work from home|wfh|dari rumah|online|virtual|digital nomad|anywhere|location independent|telecommute|hybrid|flexible)\b']
        }
        
        # Pola untuk experience level
        self.experience_patterns = {
            'Fresh Graduate': [r'\b(fresh graduate|fresh grad|lulusan baru|entry level|junior|trainee|associate|intern|magang|no experience|pemula|beginner|graduate program|management trainee)\b'],
            'Mid Level': [r'\b(mid level|middle|experienced|3-5 years|senior|specialist|coordinator|supervisor|team lead|lead|principal|expert|professional|intermediate)\b'],
            'Senior Level': [r'\b(senior|manager|head|director|vp|vice president|chief|c-level|executive|leadership|managerial|strategic|principal|architect|consultant|expert level)\b']
        }
        
        # Pola untuk work type
        self.work_type_patterns = {
            'Full Time': [r'\b(full time|fulltime|permanent|tetap|regular|staff|karyawan tetap)\b'],
            'Part Time': [r'\b(part time|parttime|paruh waktu|freelance|contract|kontrak|temporary|temp|seasonal|casual)\b'],
            'Internship': [r'\b(internship|intern|magang|trainee|apprentice|praktik kerja|pkl|co-op|work study)\b'],
            'Remote': [r'\b(remote|work from home|wfh|telecommute|virtual|online|digital nomad|hybrid|flexible)\b']
        }
        
        # Stop words bahasa Indonesia
        self.stop_words = {
            'saya', 'aku', 'kamu', 'anda', 'dia', 'mereka', 'kita', 'kami',
            'yang', 'ini', 'itu', 'dari', 'ke', 'di', 'untuk', 'dengan',
            'atau', 'dan', 'adalah', 'akan', 'sudah', 'telah', 'sedang',
            'cari', 'mencari', 'butuh', 'perlu', 'mau', 'ingin', 'bisa',
            'dapat', 'ada', 'tidak', 'jangan', 'harus', 'mesti', 'wajib',
            'tolong', 'mohon', 'bantu', 'bantuan', 'info', 'informasi',
            'tentang', 'mengenai', 'sekitar', 'kurang', 'lebih', 'sangat',
            'paling', 'terbaik', 'bagus', 'baik', 'cocok', 'sesuai'
        }
    
    def extract(self, text: str) -> Dict:
        """Extract keywords dengan confidence scoring"""
        text_lower = text.lower()
        
        # Bersihkan teks
        cleaned_text = self._clean_text(text_lower)
        
        # Extract berbagai komponen
        intent = self._extract_intent(cleaned_text)
        fields = self._extract_fields(cleaned_text)
        locations = self._extract_locations(cleaned_text)
        experience = self._extract_experience(cleaned_text)
        work_type = self._extract_work_type(cleaned_text)
        
        # Hitung confidence score
        confidence = self._calculate_confidence(intent, fields, locations)
        
        return {
            'intent': intent,
            'field': fields,
            'location': locations,
            'experience': experience,
            'work_type': work_type,
            'confidence': confidence,
            'original_text': text
        }
    
    def _clean_text(self, text: str) -> str:
        """Bersihkan teks dari karakter yang tidak perlu"""
        # Hapus karakter khusus kecuali spasi dan huruf
        text = re.sub(r'[^\w\s]', ' ', text)
        # Hapus multiple spaces
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _extract_intent(self, text: str) -> str:
        """Extract intent dari teks"""
        intent_patterns = {
            'magang': [
                r'\b(magang|internship|intern|praktik kerja|pkl|trainee|apprentice|co-op|work study)\b',
                r'\bcari.*magang\b',
                r'\bintern.*program\b',
                r'\bpraktik.*kerja\b'
            ],
            'pekerjaan': [
                r'\b(kerja|job|pekerjaan|lowongan|karir|career|work|employment|position|posisi|jabatan|staff|karyawan)\b',
                r'\bcari.*kerja\b',
                r'\blowongan.*kerja\b',
                r'\bfull.*time\b',
                r'\bpart.*time\b'
            ],
            'kursus': [
                r'\b(kursus|course|pelatihan|training|belajar|learn|study|class|workshop|seminar|bootcamp|certification|sertifikasi)\b',
                r'\bcari.*kursus\b',
                r'\bingin.*belajar\b',
                r'\bpelatihan.*online\b'
            ]
        }
        
        # Hitung score untuk setiap intent
        intent_scores = {}
        for intent, patterns in intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text))
                score += matches
            intent_scores[intent] = score
        
        # Return intent dengan score tertinggi
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        
        return 'unknown'
    
    def _extract_fields(self, text: str) -> List[str]:
        """Extract field/bidang dari teks"""
        found_fields = []
        
        for field, patterns in self.field_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    found_fields.append(field)
                    break
        
        # Jika tidak ada field yang ditemukan, coba extract manual
        if not found_fields:
            words = text.split()
            filtered_words = [word for word in words if word not in self.stop_words and len(word) > 2]
            
            # Ambil kata-kata yang mungkin field
            potential_fields = []
            for word in filtered_words:
                if word not in ['cari', 'mencari', 'butuh', 'perlu', 'mau', 'ingin']:
                    potential_fields.append(word)
            
            return potential_fields[:3]  # Maksimal 3 field
        
        return found_fields
    
    def _extract_locations(self, text: str) -> List[str]:
        """Extract lokasi dari teks"""
        found_locations = []
        
        for location, patterns in self.location_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    found_locations.append(location)
                    break
        
        return found_locations
    
    def _extract_experience(self, text: str) -> List[str]:
        """Extract experience level dari teks"""
        found_experience = []
        
        for level, patterns in self.experience_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    found_experience.append(level)
                    break
        
        return found_experience
    
    def _extract_work_type(self, text: str) -> List[str]:
        """Extract work type dari teks"""
        found_work_type = []
        
        for work_type, patterns in self.work_type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    found_work_type.append(work_type)
                    break
        
        return found_work_type
    
    def _calculate_confidence(self, intent: str, fields: List[str], locations: List[str]) -> float:
        """Hitung confidence score dari hasil ekstraksi"""
        score = 0.0
        
        # Intent score
        if intent != 'unknown':
            score += 0.4
        
        # Field score
        if fields:
            score += 0.3 * min(len(fields) / 2, 1)  # Maksimal 0.3
        
        # Location score
        if locations:
            score += 0.2 * min(len(locations) / 2, 1)  # Maksimal 0.2
        
        # Bonus untuk kombinasi lengkap
        if intent != 'unknown' and fields and locations:
            score += 0.1
        
        return min(score, 1.0)
    
    def get_search_suggestions(self, failed_keywords: Dict) -> List[str]:
        """Generate search suggestions ketika hasil kosong"""
        suggestions = []
        
        intent = failed_keywords.get('intent', 'unknown')
        fields = failed_keywords.get('field', [])
        locations = failed_keywords.get('location', [])
        
        # Saran berdasarkan intent
        if intent == 'magang':
            suggestions.extend([
                "Coba kata kunci yang lebih umum seperti 'IT', 'Marketing', 'Finance'",
                "Gunakan sinonim: 'internship', 'praktik kerja', 'trainee'",
                "Coba tanpa menyebutkan lokasi spesifik terlebih dahulu"
            ])
        elif intent == 'pekerjaan':
            suggestions.extend([
                "Gunakan kata kunci posisi yang lebih umum",
                "Coba berdasarkan industri: 'teknologi', 'perbankan', 'retail'",
                "Periksa ejaan dan gunakan bahasa Indonesia atau Inggris"
            ])
        elif intent == 'kursus':
            suggestions.extend([
                "Coba kata kunci yang lebih spesifik: 'Python', 'Digital Marketing', 'Excel'",
                "Gunakan sinonim: 'pelatihan', 'training', 'bootcamp'",
                "Cari berdasarkan kategori: 'programming', 'design', 'business'"
            ])
        
        # Saran berdasarkan field
        if not fields:
            suggestions.append("Sebutkan bidang yang diminati seperti 'IT', 'Marketing', 'Finance'")
        
        # Saran berdasarkan lokasi
        if not locations:
            suggestions.append("Coba tambahkan lokasi seperti 'Jakarta', 'Bandung', atau 'Remote'")
        
        return suggestions[:5]  # Maksimal 5 saran