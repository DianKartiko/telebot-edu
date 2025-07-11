# TELEBOT-EDUCATION

Bot Telegram ini dirancang untuk membantu mahasiswa menemukan informasi terkait **magang**, **kursus**, dan **lowongan pekerjaan**. Dengan memanfaatkan model AI canggih dan integrasi Telegram, bot ini bertujuan untuk menjadi asisten pribadi dalam meniti karir dan mengembangkan keterampilan.

---

## Daftar Isi

-   [Fitur](#fitur)
-   [Teknologi yang Digunakan](#teknologi-yang-digunakan)
-   [Instalasi](#instalasi)
    -   [Prasyarat](#prasyarat)
    -   [Langkah-langkah Instalasi](#langkah-langkah-instalasi)
        -   [Menggunakan `venv` (Direkomendasikan)](#menggunakan-venv-direkomendasikan)
        -   [Menggunakan `pipenv`](#menggunakan-pipenv)
-   [Konfigurasi](#konfigurasi)
-   [Penggunaan](#penggunaan)
-   [Struktur Proyek](#struktur-proyek)
-   [Lisensi](#lisensi)
-   [Kontak](#kontak)

---

## Fitur

-   **Pencarian Magang:** Pengguna dapat berinteraksi dengan bot untuk menemukan rekomendasi magang berdasarkan tempat, posisi, dan tipe magang (online, onsite).
-   **Rekomendasi Kursus:** Pengguna mendapatkan rekomendasi untuk kursus sehingga dapat mengembangan kemampuan mereka.
-   **Informasi Pekerjaan:** Pengguna dapat mengakses informasi sesuai dengan minat dan kualifikasi pekerjaan.
-   **Model AI SeaLLMs/SeaLLMs-v3-7B-Chat:** Memberikan respon yang cerdas dan relevan berdasarkan input pengguna. Mendukung berbagai bahasa yang berada di South East Asian seperti bahasa Inggris, Indonesia, Malaysia, Brunei, dsb.
-   **Interaksi Intuitif:** Antarmuka pengguna yang ramah melalui Telegram.

---

## Teknologi yang Digunakan

-   **Model AI:** SeaLLMs/SeaLLMs-v3-7B-Chat
-   **Bahasa Pemrograman:** Python 3.10+
-   **Library Utama:** `python-telegram-bot` v.20
-   **Manajemen Lingkungan Virtual:** `venv` (Direkomendasikan), `pipenv` (Sedang digunakan)

---

## Instalasi

Ikuti langkah-langkah di bawah ini untuk menyiapkan dan menjalankan bot di lingkungan lokal Anda.

### Prasyarat

Pastikan Anda telah menginstal yang berikut ini sebelum melanjutkan:

-   **Python 3.10 atau lebih baru**: Anda dapat mengunduhnya dari [situs web resmi Python](https://www.python.org/downloads/).
-   **Akses ke Internet**: Untuk mengunduh dependensi dan berinteraksi dengan API Telegram/SeaLLMs.
-   **Virtual Environment** : Anda dapat menggunakan virtual environtment sesuai kebutuhan anda seperti venv (sederhana dan mudah dikonfigurasi) atau pipenv (menggunakan konfigurasi lebih lanjut)

### Langkah-langkah Instalasi

Anda dapat memilih metode instalasi menggunakan `venv` atau `pipenv`. Metode `venv` lebih direkomendasikan karena kesederhanaannya.

#### Menggunakan `venv` (Direkomendasikan)

1.  **Klon Repositori:**
    Pertama, klon repositori proyek ini ke mesin lokal Anda:

    ```bash
    git clone [https://github.com/namapenggunaanda/nama-repositori-anda.git](https://github.com/namapenggunaanda/nama-repositori-anda.git)
    cd nama-repositori-anda
    ```

    _(Ganti `nama pengguna anda` dan `nama-repositori-anda` dengan informasi repositori Anda.)_

2.  **Buat Lingkungan Virtual:**
    Buat lingkungan virtual baru:

    ```bash
    python3.10 -m venv venv
    ```

3.  **Aktifkan Lingkungan Virtual:**

    -   **Di macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
    -   **Di Windows (Command Prompt):**
        ```bash
        venv\Scripts\activate.bat
        ```
    -   **Di Windows (PowerShell):**
        ```bash
        venv\Scripts\Activate.ps1
        ```

4.  **Instal Dependensi:**
    Setelah lingkungan virtual aktif, instal semua dependensi yang diperlukan dari `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```
    _(Pastikan Anda memiliki file `requirements.txt` di root proyek Anda. Jika belum, Anda bisa membuatnya dengan `pip freeze > requirements.txt` setelah menginstal semua library secara manual.)_

#### Menggunakan `pipenv`

1.  **Instal `pipenv` (jika belum ada):**

    ```bash
    pip install pipenv
    ```

    Konfigurasi pipenv di dalam editEnvironmentVariable dan masukkan path pipenv keadalm environmetn variable.

2.  **Klon Repositori:**

    ```bash
    git clone [https://github.com/namapenggunaanda/nama-repositori-anda.git](https://github.com/namapenggunaanda/nama-repositori-anda.git)
    cd nama-repositori-anda
    ```

3.  **Instal Dependensi dengan `pipenv`:**
    Dari direktori proyek, `pipenv` akan secara otomatis membuat lingkungan virtual dan menginstal dependensi dari `Pipfile` atau `Pipfile.lock`:

    ```bash
    pipenv install
    ```

    _(Jika Anda belum memiliki `Pipfile`, Anda bisa menambahkannya secara manual atau `pipenv install nama-library` akan membuatnya untuk Anda. Kemudian `pipenv lock -r > requirements.txt` untuk membuat `requirements.txt` jika diperlukan.)_

4.  **Aktifkan Lingkungan Shell `pipenv`:**
    Untuk menjalankan skrip Anda di lingkungan ini:
    ```bash
    pipenv shell
    ```

---

## Konfigurasi

Sebelum menjalankan bot, Anda perlu mengatur beberapa variabel lingkungan atau file konfigurasi.

1.  **Dapatkan Token Bot Telegram:**

    -   Buka Telegram dan cari [@BotFather](https://t.me/BotFather).
    -   Gunakan perintah `/newbot` dan ikuti instruksi untuk mendapatkan token bot Anda.
    -   Simpan token ini dengan aman.
    
    **Notes**
    -   Untuk pengembangan bersama, silahkan diskusikan dengan team pengembang untuk diberikan akses kedalam API yang dibutuhkan.

2.  **Konfigurasi Model AI (SeaLLMs):**

    -   Untuk konfigurasi Model AI (SeaLLMs), kalian bisa mendaftarkan akun untuk mendapatkan hugging face token dan konfigurasikan dengan model yang anda pilih.
    -   Penggunaan model AI SeaLLMs bisa menggunakan metode inference providers, kalian bisa gunakan bahasa pemrograman yang dibutuhkan seperti python, javascripts, dan cURL. Dapat menggunakan huggingface_hub, requests, dan openai, saat ini team pengembang menggunakan requests karena kesederhanaannya dan kalian akan mendapat API_URL dari model AI.

    **Notes**
    -   Untuk pengembangan bersama, silahkan diskusikan dengan team pengembang untuk diberikan akses kedalam API yang dibutuhkan.

3.  **Buat File `.env`:**

    **Instalasi library python-dotenv:**

    ```bash
    pip install python-dotenv
    ```

    Buat file bernama `.env` di root direktori proyek Anda dan tambahkan variabel-variabel berikut:

    ```ini
    TELEGRAM_BOT_TOKEN="GANTI_DENGAN_TOKEN_BOT_ANDA"
    SEALLMS_API_KEY="GANTI_DENGAN_API_KEY_SEALLMS_ANDA" # Jika diperlukan
    # Variabel konfigurasi lain yang mungkin Anda miliki, contoh:
    # DATABASE_URL="postgresql://user:password@host:port/database"
    ```

    -   Pastikan Anda tidak mempublikasikan file `.env` ini ke repositori publik Anda (tambahkan `.env` ke `.gitignore`).

---

## Penggunaan

Setelah instalasi dan konfigurasi, Anda dapat menjalankan bot.

1.  **Aktifkan Lingkungan Virtual (jika belum):**

    -   Jika menggunakan `venv`:
        ```bash
        source venv/bin/activate
        ```
    -   Jika menggunakan `pipenv`:
        ```bash
        pipenv shell
        ```

2.  **Jalankan Bot:**

    ```bash
    python main.py # Atau nama file utama bot Anda
    ```

    Bot sekarang akan berjalan dan siap menerima perintah di Telegram.

---

## Struktur Proyek

Berikut adalah gambaran umum struktur direktori proyek ini:

    TELEBOT/
    ├── venv/                       # Lingkungan virtual Python (jika menggunakan venv)
    ├── Pipfile                     # Konfigurasi pipenv (jika menggunakan pipenv)
    ├── Pipfile.lock                # Kunci dependensi pipenv
    ├── requirements.txt            # Daftar dependensi Python
    ├── .env                        # File .env (simpan nilai sensitif, TIDAK di-commit ke Git)
    ├── .gitignore                  # File yang diabaikan oleh Git (pastikan .env ada di sini)
    ├── main.py                     # Skrip utama untuk menjalankan bot
    ├── bot/                        # Direktori utama untuk semua logika inti bot Telegram
    │ ├── **init**.py               # Mengidentifikasi 'bot' sebagai Python package
    │ ├── dispatcher.py             # Logika untuk inisiasi sebuah perintah
    │ ├── handlers/                 # Direktori untuk handler perintah Telegram
    │ │ ├── **init**.py             # Mengidentifikasi 'handlers' sebagai Python package
    │ │ ├── handlers.py             # Handler untuk perintah `/start`, `/help`, /info, dll.
    │ │ └── message_handlers.py     # (Baru) Handler untuk pesan teks biasa, dll.
    │ ├── scraper/                  # Direktori untuk program scraping data
    │ │ ├── **init**.py             # Mengidentifikasi 'scraper' sebagai Python package
    │ │ └── data_scraper.py         # Logika utama untuk scraping data
    │ ├── utils/                    # Direktori untuk fungsi utilitas umum
    │ │ ├── **init**.py             # Mengidentifikasi 'utils' sebagai Python package
    │ │ ├── database.py             # Modul untuk interaksi dengan database (SQLite, MySQL dll.)
    │ │ ├── keywords_extraction.py  # Fungsi untuk ekstraksi kata kunci
    │ │ ├── llm_integration.py      # Modul untuk interaksi dengan SeaLLMs
    │ │ └── logger.py               # Modul untuk logging aplikasi
    │ ├── database/                 # Direktori untuk file database lokal (jika ada)
    │ │ ├── bot.db                  # (Perubahan Nama) Contoh file database SQLite
    └── README.md                   # File dokumentasi proyek

---
## Kontak

Punya pertanyaan atau ingin berdiskusi? Jangan sungkan untuk menghubungi!

[![LinkedIn](https://img.shields.io/badge/-LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/dian-wicaksono/)
[![Email](https://img.shields.io/badge/-Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:auliakartiko28@gmail.com)
