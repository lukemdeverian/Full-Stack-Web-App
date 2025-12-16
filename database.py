import sqlite3
from datetime import datetime

DB_PATH = 'codescan.db'

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            language TEXT NOT NULL,
            upload_date TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

def save_file(filename, language):
    conn = get_connection()
    cursor = conn.cursor()
    upload_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(
        'INSERT INTO files (filename, language, upload_date) VALUES (?, ?, ?)',
        (filename, language, upload_date)
    )
    file_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return file_id

def get_all_files():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM files ORDER BY upload_date DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_file_by_id(file_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM files WHERE id = ?', (file_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_file(file_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM files WHERE id = ?', (file_id,))
    conn.commit()
    conn.close()