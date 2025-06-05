import schedule 
import time 
from bot.scraper.scraping import scrape_data
from dotenv import load_dotenv
import os

URL = os.getenv('KALIBRR_URL')

def job():
    try: 
        print('Menjalankan Scraping . . .')
        scrape_data(URL)
        print('Scraping selesal\n')
    except Exception as e:
        print(f"Scrapping tidak berhasil: {e}")

schedule.every(6).hours.do(job)

print("Scheduler berjalan... (Ctrl+C untuk berhenti)")
job()  # Run sekali saat start

while True:
    schedule.run_pending()
    time.sleep(60)  # cek tiap menit
