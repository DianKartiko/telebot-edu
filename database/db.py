import sqlite3
from datetime import datetime
import logging

DB_NAME = 'history_chat.db'

def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Table chat history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history_chat (
            user_id INTEGER,
            user_input TEXT,
            bot_response TEXT,
            timestamp TEXT
        )
''')

    conn.commit()
    conn.close()

