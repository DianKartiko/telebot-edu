class PromptEngine:
    @staticmethod
    def parse_input(text):
        """Analisis pesan user untuk ekstrak:
        - Intent (cari magang/kursus)
        - Parameter (lokasi, keyword, dll)
        """
        text = text.lower().strip()
        
        # Deteksi intent
        intent = None
        if "magang" in text or "internship" in text or "intern" in text:
            intent = "magang"
        elif "kursus" in text or "course" in text:
            intent = "kursus"
        elif "kerja" in text or "jobs" in text or "job" in text:
            intent = "kerja"
        
        # Ekstrak parameter
        params = {}
        if "jakarta" in text:
            params["lokasi"] = "Jakarta"
        elif "bandung" in text:
            params["lokasi"] = "Bandung"
        elif "yogyakarta" in text:
            params['lokasi'] = "Yogyakarta"
        elif "tangerang" in text:
            params['lokasi'] = "Tangerang"
        
        # Ambil keyword bebas (contoh: "magang IT")
        if intent:
            keyword = text.replace("magang", "").replace("kursus", "").replace("kerja", "").strip()
            if keyword:
                params["keyword"] = keyword
        
        return {"intent": intent, "params": params}

    @staticmethod
    def format_results(intent, results):
        """Format hasil pencarian untuk ditampilkan di Telegram"""
        if not results:
            return "❌ Tidak ditemukan hasil. Coba kata kunci lain."
        
        if intent == "magang":
            message = "🔍 <b>Hasil Magang:</b>\n\n"
            for item in results:
                message += (
                    f"🏢 <b>{item['perusahaan']}</b>\n"
                    f"📌 {item['posisi']} ({item['lokasi']})\n"
                    f"💰 Gaji: {item['gaji']}\n"
                    f"⏳ Deadline: {item['deadline']}\n\n"
                )
            return message
        
        elif intent == "kursus":
            print("Debug - Results Structure:", results)
            message = "🔍 <b>Hasil Kursus:</b>\n\n"
            for item in results:
                message += (
                    f"🏢 <b>{item['title']}</b>\n"
                    f"📌 {item['duration']} ({item['module_total']})\n"
                    f"⏳ Level: {item['level']}\n\n"
                )
            return message

        elif intent == "kerja":
            message = "🔍 <b>Hasil Kerja:</b>\n\n"
            for item in results:
                message += (
                    f"🏢 <b>{item['perusahaan']}</b>\n"
                    f"📌 {item['posisi']} ({item['lokasi']})\n"
                    f"💰 Gaji: {item['gaji']}\n"
                    f"⏳ Tipe Perkejaan: {item['job_type']}\n\n"
                )
            return message
    
        else:
            return "ℹ️ Fitur pencarian kursus belum tersedia."