import sqlite3
from datetime import datetime
from pathlib import Path
import os
from dotenv import load_dotenv

# Load konfigurasi dari .env
load_dotenv()

class DatabaseIntern:
    def __init__(self):
        self.db_path = Path(os.getenv("DB_INTERN"))
        self.db_path.parent.mkdir(exist_ok=True)  # Buat folder jika belum ada
        self._init_db()

    def _init_db(self):
        """Buat tabel jika belum ada"""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS magang (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sumber TEXT NOT NULL,
                    perusahaan TEXT NOT NULL,
                    posisi TEXT NOT NULL,
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
        if not data:
            return
        
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

class DatabaseJob:
    def __init__(self):
        self.db_path = Path(os.getenv('DB_JOB'))
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Buat tabel jika belum ada"""
        with self._get_connection() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sumber TEXT,
            perusahaan TEXT,
            posisi TEXT,
            lokasi TEXT,
            gaji TEXT,
            job_type TEXT,
            tanggal_scrape TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(perusahaan, posisi) 
            )
        """)

    def _get_connection(self):
        """Koneksi ke SQLite dengan hasil berupa dictionary"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def save_jobs(self, data):
        """Simpan data magang dari Glints"""
        with self._get_connection() as conn:
            conn.executemany("""
        INSERT OR IGNORE INTO jobs
        (sumber, perusahaan, posisi, lokasi, gaji, job_type) 
        VALUES (?, ?, ?, ?, ?, ?)
        """, [
            (
                item['sumber'],
                item['perusahaan'],
                item['posisi'],
                item['lokasi'],
                item['gaji'],
                item['job_type'],
            ) for item in data
        ])

        conn.commit()

    def search_job(self, keyword=None, limit=5):
        """Cari pekerjaan berdasarkan keyword (posisi/lokasi)"""
        with self._get_connection() as conn:
            if keyword:
                cursor = conn.execute("""
                    SELECT * FROM jobs 
                    WHERE posisi LIKE ? OR lokasi LIKE ?
                    ORDER BY tanggal_scrape DESC 
                    LIMIT ?
                """, (f"%{keyword}%", f"%{keyword}%", limit))
            else:
                cursor = conn.execute("""
                    SELECT * FROM jobs 
                    ORDER BY tanggal_scrape DESC 
                    LIMIT ?
                """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

class DatabaseCourse:
    def __init__(self):
        self.db_path = Path(os.getenv('DB_COURSE'))
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS courses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sumber TEXT,
                    title TEXT,
                    duration TEXT,
                    module_total TEXT,
                    tanggal_scrape TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(title, duration) 
                )
            """)
            conn.commit()

    def _get_connection(self):
        """Koneksi ke SQLite dengan hasil berupa dictionary"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
            
    def save_courses(self, data):  # Ubah nama method untuk konsistensi
        """Simpan data course dari Dicoding"""
        if not data:
            return
            
        with self._get_connection() as conn:
            conn.executemany("""
                INSERT OR IGNORE INTO courses  # Perbaikan: courses bukan jobs
                (sumber, title, duration, module_total) 
                VALUES (?, ?, ?, ?)
            """, [
                (
                    item['sumber'],
                    item['title'],
                    item['duration'],
                    item['module_total'],
                ) for item in data
            ])
            conn.commit()

    def search_course(self, keyword=None, limit=5):  # Perbaikan typo seacrh -> search
        """Cari course berdasarkan keyword (title/duration)"""
        with self._get_connection() as conn:
            if keyword:
                cursor = conn.execute("""
                    SELECT * FROM courses 
                    WHERE title LIKE ? OR duration LIKE ?
                    ORDER BY tanggal_scrape DESC 
                    LIMIT ?
                """, (f"%{keyword}%", f"%{keyword}%", limit))
            else:
                cursor = conn.execute("""
                    SELECT * FROM courses 
                    ORDER BY tanggal_scrape DESC 
                    LIMIT ?
                """, (limit,))
            return [dict(row) for row in cursor.fetchall()]