import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from bot.utils.database import DatabaseIntern, DatabaseJob, DatabaseCourse

load_dotenv()

logger = logging.getLogger(__name__)

class BaseScraper:
    def __init__(self, db, url):
        self.db = db
        self.url = url
        self.delay = float(os.getenv("SCRAPER_DELAY", 2))
        self.driver = None
        self.source_name = "Base"  # Override di child class

    def _init_webdriver(self):
        """Setup Selenium Chrome WebDriver"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument('--user-agent=Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36')
        
        try:
            return webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
        except Exception as e:
            logger.error(f"Gagal inisialisasi WebDriver: {str(e)}")
            raise

    def _extract_data(self, soup):
        """Method abstract untuk ekstrak data (harus diimplement child class)"""
        raise NotImplementedError

    def scrape(self):
        """Main scraping method"""
        try:
            logger.info(f"🔄 Memulai scraping {self.source_name}...")
            
            # Inisialisasi driver di sini
            self.driver = self._init_webdriver()
            self.driver.get(self.url)
            
            # Tunggu sampai konten muncul dengan timeout lebih lama
            wait_element = self._get_wait_element()
            logger.info(f"⏳ Menunggu elemen: {wait_element}")
            
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f".{wait_element}"))
            )
            
            # Scroll sedikit untuk memastikan semua konten ter-load
            self.driver.execute_script("window.scrollTo(0, 500);")
            time.sleep(2)
            
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            results = self._extract_data(soup)
            
            logger.info(f"✅ Berhasil scrape {len(results)} data dari {self.source_name}")
            return results

        except Exception as e:
            logger.error(f"❌ Gagal scraping {self.source_name}: {str(e)}", exc_info=True)
            return []
        finally:
            if self.driver:
                self.driver.quit()
            time.sleep(self.delay)

    def _get_wait_element(self):
        """Class CSS untuk wait element (override di child class)"""
        raise NotImplementedError

class KalibrrScraper(BaseScraper):
    def __init__(self, db):
        super().__init__(db, os.getenv("KALIBRR_URL"))
        self.source_name = "Kalibrr"

    def _get_wait_element(self):
        return "css-1otdiuc"

    def _extract_data(self, soup):
        internships = []
        
        # Cek beberapa kemungkinan selector
        selectors = [
            "div.css-1otdiuc",
            "div[class*='JobCard']",
            "div[class*='job-card']",
        ]
        
        items = []
        for selector in selectors:
            items = soup.select(selector)
            if items:
                logger.info(f"✅ Menggunakan selector: {selector} - {len(items)} items")
                break
        
        if not items:
            logger.warning("❌ Tidak ada job items ditemukan dengan selector yang ada")
            # Debug: tampilkan beberapa class yang ada
            all_divs = soup.find_all("div", class_=True)[:10]
            logger.info("🔍 Beberapa class div yang ditemukan:")
            for div in all_divs:
                logger.info(f"   - {div.get('class')}")
            return []
        
        for item in items:
            try:
                # Coba beberapa cara ekstraksi
                perusahaan = self._safe_extract(item, 'a', 'k-text-subdued k-font-bold') or \
                           self._safe_extract(item, 'span', 'k-text-subdued') or \
                           self._extract_by_contains(item, 'company')
                
                posisi = self._safe_extract(item, 'h2', 'css-1gzvnis') or \
                        self._safe_extract(item, 'h3') or \
                        self._extract_by_contains(item, 'title')
                
                lokasi = self._safe_extract(item, 'span', 'k-text-gray-500 k-block k-pointer-events-none') or \
                        self._extract_by_contains(item, 'location')
                
                gaji = self._safe_extract(item, 'p', 'k-text-gray-500') or "Tidak disebutkan"
                
                deadline = self._safe_extract(item, 'span', "k-text-xs k-font-bold k-text-gray-600") or "Tidak ada"
                
                data = {
                    'sumber': self.source_name,
                    'perusahaan': perusahaan,
                    'posisi': posisi,
                    'lokasi': lokasi,
                    'gaji': gaji,
                    'deadline': deadline
                }
                
                # Hanya simpan jika ada perusahaan dan posisi (field penting)
                if data['perusahaan'] and data['posisi']:
                    internships.append(data)
                    logger.debug(f"📋 Data: {data['perusahaan']} - {data['posisi']}")

            except Exception as e:
                logger.warning(f"Gagal parsing item: {str(e)}")
                continue
        
        return internships

    def _safe_extract(self, parent, tag, class_=None):
        """Helper untuk ekstrak text dengan aman"""
        try:
            if class_:
                elem = parent.find(tag, class_=class_)
            else:
                elem = parent.find(tag)
            return elem.text.strip() if elem else None
        except:
            return None
    
    def _extract_by_contains(self, parent, keyword):
        """Ekstrak berdasarkan keyword dalam class atau text"""
        try:
            for elem in parent.find_all():
                if elem.get('class'):
                    class_str = ' '.join(elem.get('class'))
                    if keyword.lower() in class_str.lower():
                        return elem.text.strip()
            return None
        except:
            return None
    
class GlintsScraper(BaseScraper):
    def __init__(self, db):
        super().__init__(db, os.getenv("GLINTS_URL"))
        self.source_name = "Glints"

    def _get_wait_element(self):
        return "JobCardsc__JobCardWrapper-sc-hmqj50-1"

    def _extract_data(self, soup):
        jobs = []
        
        # Coba beberapa selector untuk Glints
        selectors = [
            "div.JobCardsc__JobCardWrapper-sc-hmqj50-1",
            "div[class*='JobCard']",
            "div[class*='CompactOpportunityCard']",
            "article[class*='JobCard']"
        ]
        
        items = []
        for selector in selectors:
            items = soup.select(selector)
            if items:
                logger.info(f"✅ Menggunakan selector: {selector} - {len(items)} items")
                break
        
        if not items:
            logger.warning("❌ Tidak ada job items ditemukan dengan selector yang ada")
            return []
        
        for item in items:
            try:
                perusahaan = self._safe_extract(item, 'a', 'CompactOpportunityCardsc__CompanyLink-sc-dkg8my-14') or \
                           self._extract_by_contains(item, 'company')
                
                posisi = self._safe_extract(item, 'h2', 'CompactOpportunityCardsc__JobTitle-sc-dkg8my-11') or \
                        self._safe_extract(item, 'h3') or \
                        self._extract_by_contains(item, 'title')
                
                lokasi = self._safe_extract(item, 'div', 'CardJobLocation__LocationWrapper-sc-v7ofa9-0') or \
                        self._extract_by_contains(item, 'location')
                
                gaji = self._safe_extract(item, 'span', 'CompactOpportunityCardsc__NotDisclosedMessage-sc-dkg8my-27') or \
                      "Tidak disebutkan"
                
                job_type = self._safe_extract(item, 'div', 'TagStyle__TagContentWrapper-sc-r1wv7a-1') or \
                          "Full-time"
                
                data = {
                    'sumber': self.source_name,
                    'perusahaan': perusahaan,
                    'posisi': posisi,
                    'lokasi': lokasi,
                    'gaji': gaji,
                    'job_type': job_type,
                }
                
                # Hanya simpan jika ada perusahaan dan posisi
                if data['perusahaan'] and data['posisi']:
                    jobs.append(data)
                    logger.debug(f"📋 Data: {data['perusahaan']} - {data['posisi']}")

            except Exception as e:
                logger.warning(f"Gagal parsing item: {str(e)}")
                continue
        
        return jobs

    def _safe_extract(self, parent, tag, class_=None):
        """Helper untuk ekstrak text dengan aman"""
        try:
            if class_:
                elem = parent.find(tag, class_=class_)
            else:
                elem = parent.find(tag)
            return elem.text.strip() if elem else None
        except:
            return None
    
    def _extract_by_contains(self, parent, keyword):
        """Ekstrak berdasarkan keyword dalam class atau text"""
        try:
            for elem in parent.find_all():
                if elem.get('class'):
                    class_str = ' '.join(elem.get('class'))
                    if keyword.lower() in class_str.lower():
                        return elem.text.strip()
            return None
        except:
            return None

class CourseScraper(BaseScraper):
    def __init__(self, db):
        super().__init__(db, os.getenv("DICODING_URL"))
        self.source_name = "Dicoding"
    
    def _get_wait_element(self):
        return "course-card"  # Class yang lebih umum untuk waiting
    
    def _extract_data(self, soup):
        courses = []
        
        # Coba beberapa selector untuk handling perubahan UI
        course_selectors = [
            'a.course-card',  # Selector utama
            'div[class*="course-card"]',  # Fallback 1
            'article[class*="course"]'  # Fallback 2
        ]
        
        course_items = []
        for selector in course_selectors:
            course_items = soup.select(selector)
            if course_items:
                logger.info(f"✅ Menggunakan selector: {selector} - {len(course_items)} items ditemukan")
                break
        
        if not course_items:
            logger.warning("❌ Tidak ada course items ditemukan dengan selector yang ada")
            return []
        
        for item in course_items:
            try:
                # Ekstrak data dengan fallback yang lebih robust
                title = self._safe_extract(item, 'h5', 'course-card__name') or \
                        self._extract_by_contains(item, 'title') or \
                        self._safe_extract(item, 'h3') or \
                        self._safe_extract(item, 'h2')
                
                duration = self._safe_extract(item, 'span', 'mr-2') or \
                            self._extract_by_contains(item, 'duration')
                
                module_total = self._safe_extract(item, 'span', 'mr-3') or \
                                self._extract_by_contains(item, 'module')
                
                level = self._safe_extract(item, 'span', 'course-card__level') or \
                        self._extract_by_contains(item, 'level')
                
                # Pastikan data minimal yang diperlukan ada
                if not title:
                    continue
                    
                courses.append({
                    'sumber': self.source_name,
                    'title': title.strip(),
                    'duration': duration.strip() if duration else 'Tidak disebutkan',
                    'module_total': module_total.strip() if module_total else 'Tidak disebutkan',
                    'level': level.strip() if level else 'Pemula',
                })
                
                logger.debug(f"📚 Course ditemukan: {title}")

            except Exception as e:
                logger.warning(f"Gagal parsing course item: {str(e)}")
                continue
        
        logger.info(f"✅ Berhasil scrape {len(courses)} courses")
        return courses

    def _safe_extract(self, parent, tag, class_=None):
        """Helper untuk ekstrak text dengan aman"""
        try:
            if class_:
                elem = parent.find(tag, class_=class_)
            else:
                elem = parent.find(tag)
            return elem.text.strip() if elem else None
        except:
            return None
    
    def _extract_by_contains(self, parent, keyword):
        """Ekstrak berdasarkan keyword dalam class atau text"""
        try:
            for elem in parent.find_all():
                if elem.get('class'):
                    class_str = ' '.join(elem.get('class'))
                    if keyword.lower() in class_str.lower():
                        return elem.text.strip()
            return None
        except:
            return None
        
def run_scrapers():
    """Jalankan semua scraper"""
    logger.info("🚀 Memulai proses scraping...")
    
    try:
        db_intern = DatabaseIntern()
        db_job = DatabaseJob()
        db_courses = DatabaseCourse()
        
        scrapers = [
            KalibrrScraper(db_intern),
            GlintsScraper(db_job),
            CourseScraper(db_courses)
        ]
        
        total_saved = 0
        
        for scraper in scrapers:
            try:
                logger.info(f"🔄 Menjalankan {scraper.source_name} scraper...")
                data = scraper.scrape()
                
                if data:
                    if isinstance(scraper, KalibrrScraper):
                        scraper.db.save_magang(data)
                        total_saved += len(data)
                    elif isinstance(scraper, GlintsScraper):
                        scraper.db.save_jobs(data)
                        total_saved += len(data)
                    elif isinstance(scraper, CourseScraper):
                        scraper.db.save_courses(data)
                        total_saved += len(data)
                else:
                    logger.warning(f"⚠️  Tidak ada data dari {scraper.source_name}")
                    
            except Exception as e:
                logger.error(f"❌ Gagal menjalankan {scraper.source_name}: {str(e)}", exc_info=True)
        
        logger.info(f"✅ Selesai! Total {total_saved} data berhasil disimpan")
        return total_saved
        
    except Exception as e:
        logger.error(f"❌ Error fatal dalam run_scrapers: {str(e)}", exc_info=True)
        return 0
