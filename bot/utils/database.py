import sqlite3
import logging
from datetime import datetime
from pathlib import Path
import os
from dotenv import load_dotenv

# Load konfigurasi dari .env
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.db_path = Path(os.getenv("DB_PATH"))
        self.db_path.parent.mkdir(exist_ok=True)  # Buat folder jika belum ada
        self._init_db()

    def _init_db(self):
        """Buat tabel jika belum ada"""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS magang (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sumber TEXT,
                    perusahaan TEXT,
                    posisi TEXT,
                    lokasi TEXT,
                    gaji TEXT,
                    deadline TEXT,
                    tanggal_scrape TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(perusahaan, posisi)  
                )
            """)
            conn.commit()

    def _get_connection(self):
        """Koneksi ke SQLite dengan hasil berupa dictionary"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def save_magang(self, data):
        """Simpan data magang dari Kalibrr"""
        with self._get_connection() as conn:
            conn.executemany("""
                INSERT OR IGNORE INTO magang 
                (sumber, perusahaan, posisi, lokasi, gaji, deadline)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [
                (
                    item['sumber'],
                    item['perusahaan'],
                    item['posisi'],
                    item['lokasi'],
                    item['gaji'],
                    item['deadline'],
                ) for item in data
            ])
            conn.commit()

    def search_magang(self, keyword=None, limit=5):
        """Cari magang berdasarkan keyword (posisi/lokasi)"""
        with self._get_connection() as conn:
            if keyword:
                cursor = conn.execute("""
                    SELECT * FROM magang 
                    WHERE posisi LIKE ? OR lokasi LIKE ?
                    ORDER BY tanggal_scrape DESC 
                    LIMIT ?
                """, (f"%{keyword}%", f"%{keyword}%", limit))
            else:
                cursor = conn.execute("""
                    SELECT * FROM magang 
                    ORDER BY tanggal_scrape DESC 
                    LIMIT ?
                """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
