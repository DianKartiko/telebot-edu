import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import os
from dotenv import load_dotenv

# Load konfigurasi dari .env
load_dotenv()

def init_databases():
    """Initialize database directories and paths"""
    data_dir = Path(os.environ.get('DATABASE_PATH', './database/'))
    data_dir.mkdir(exist_ok=True)
    
    # Set default database paths jika environment variables tidak ada
    if not os.getenv('DB_INTERN'):
        os.environ['DB_INTERN'] = str(data_dir / 'intern.db')
    if not os.getenv('DB_JOB'):
        os.environ['DB_JOB'] = str(data_dir / 'job.db')
    if not os.getenv('DB_COURSE'):
        os.environ['DB_COURSE'] = str(data_dir / 'course.db')

class DatabaseIntern:
    def __init__(self):
        # Pastikan database directories sudah diinisialisasi
        init_databases()
        self.db_path = Path(os.getenv("DB_INTERN"))
        self.db_path.parent.mkdir(exist_ok=True)
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

    def search_magang(self, keyword: str = "", location: str = "", limit: int = 5) -> List[Dict]:
        """Cari magang dengan parameter yang aman"""
        with self._get_connection() as conn:
            params = []
            query = "SELECT * FROM magang"
            
            # Bangun klausa WHERE dinamis
            conditions = []
            if keyword:
                conditions.append("(posisi LIKE ? OR perusahaan LIKE ? OR gaji LIKE ?)")
                params.extend([f"%{keyword}%"] * 3)
            if location:
                conditions.append("lokasi LIKE ?")
                params.append(f"%{location}%")
                
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            query += " ORDER BY tanggal_scrape DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

class DatabaseJob:
    def __init__(self):
        init_databases()
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
            conn.commit()

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

    def search_jobs(self, keyword: str = "", location: str = "", limit: int = 5) -> List[Dict]:
        """Cari magang dengan parameter yang aman"""
        with self._get_connection() as conn:
            params = []
            query = "SELECT * FROM jobs"
            
            # Bangun klausa WHERE dinamis
            conditions = []
            if keyword:
                conditions.append("(posisi LIKE ? OR perusahaan LIKE ? OR gaji LIKE ?)")
                params.extend([f"%{keyword}%"] * 3)
            if location:
                conditions.append("lokasi LIKE ?")
                params.append(f"%{location}%")
                
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            query += " ORDER BY tanggal_scrape DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

class DatabaseCourse:
    def __init__(self):
        init_databases()
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
    
    def save_courses(self, data):
        """Simpan data course dari Dicoding"""
        if not data:
            return
            
        with self._get_connection() as conn:
            conn.executemany("""
                INSERT OR IGNORE INTO courses 
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

    def search_course(self, keyword: str = "", limit: int = 5) -> List[Dict]:
        """Implementasi untuk kursus (tanpa lokasi)"""
        with self._get_connection() as conn:
            query = "SELECT * FROM courses"
            params = []
            
            if keyword:
                query += " WHERE (title LIKE ? OR sumber LIKE ? OR duration LIKE ?)"
                params.extend([f"%{keyword}%"] * 3)
                
            query += " ORDER BY tanggal_scrape DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
