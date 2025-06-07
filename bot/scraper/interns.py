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
from bot.utils.database import DatabaseIntern

load_dotenv()

logger = logging.getLogger(__name__)

class KalibrrScraper:
    def __init__(self):
        self.db = DatabaseIntern()
        self.url = os.getenv("KALIBRR_URL")
        self.delay = float(os.getenv("SCRAPER_DELAY"))
        self.driver = self._init_webdriver()

    def _init_webdriver(self):
        """Setup Selenium Chrome WebDriver"""
        options = Options()
        options.add_argument("--headless")  # Run tanpa GUI
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Untuk deployment (pastikan ChromeDriver ada di PATH)
        try:
            return webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
        except Exception as e:
            logger.error(f"Gagal inisialisasi WebDriver: {str(e)}")
            raise

    def scrape(self):
        """Ambil data magang dari Kalibrr"""
        try:
            logger.info("🔄 Memulai scraping Kalibrr...")
            self.driver.get(self.url)
            
            # Tunggu sampai daftar magang muncul
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "css-1otdiuc"))
            )
            
            # Parsing dengan BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            internships = []
            
            for item in soup.find_all("div", class_="css-1otdiuc"):
                try:
                    # Pastikan semua elemen ada sebelum mengambil text
                    company_elem = item.find('a', class_='k-text-subdued k-font-bold')
                    position_elem = item.find('h2', class_='css-1gzvnis')
                    location_elem = item.find('span', class_='k-text-gray-500 k-block k-pointer-events-none')
                    salary_elem = item.find('p', class_='k-text-gray-500')
                    deadline_elem = item.find('span', class_='k-text-xs k-font-bold k-text-gray-600')

                # Validasi elemen
                    if not all([company_elem, position_elem, location_elem]):
                        continue

                    internships.append({
                        'sumber': 'Kalibrr',
                        'perusahaan': company_elem.text.strip() if company_elem else 'Tidak disebutkan',
                        'posisi': position_elem.text.strip() if position_elem else 'Tidak disebutkan',
                        'lokasi': location_elem.text.strip() if location_elem else 'Tidak disebutkan',
                        'gaji': salary_elem.text.strip() if salary_elem else 'Tidak disebutkan',
                        'deadline': deadline_elem.text.strip() if deadline_elem else 'Tidak disebutkan',
                    })

                except AttributeError as e:
                    logger.warning(f"Data tidak lengkap: {e}")
                    continue
            
            logger.info(f"✅ Berhasil scrape {len(internships)} data magang")
            return internships

        except Exception as e:
            logger.error(f"❌ Gagal scraping: {e}")
            return []
        finally:
            time.sleep(self.delay)
            self.driver.quit()

    def _get_detail_url(self, soup_item):
        """Dapatkan URL detail magang (jika ada)"""
        # Kalibrr menggunakan JavaScript, jadi URL halaman sama
        return self.url

def run_scraper():
    """Jalankan scraping dan simpan ke database"""
    scraper = KalibrrScraper()
    data = scraper.scrape()
    if data:
        scraper.db.save_magang(data)
    return data