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

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            severity TEXT NOT NULL,
            line_number INTEGER NOT NULL,
            code TEXT NOT NULL,
            description TEXT NOT NULL,
            cwe TEXT NOT NULL,
            rule_id TEXT NOT NULL,
            FOREIGN KEY (file_id) REFERENCES files(id)
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

def save_findings(findings):
    if not findings:
        return
    conn = get_connection()
    cursor = conn.cursor()
    for f in findings:
        cursor.execute(
            '''INSERT INTO findings
               (file_id, title, severity, line_number, code, description, cwe, rule_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (f['file_id'], f['title'], f['severity'], f['line_number'],
             f['code'], f['description'], f['cwe'], f['rule_id'])
        )
    conn.commit()
    conn.close()

def get_all_files():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT
            files.id,
            files.filename,
            files.language,
            files.upload_date,
            COUNT(findings.id) as findings_count
        FROM files
        LEFT JOIN findings ON files.id = findings.file_id
        GROUP BY files.id
        ORDER BY files.upload_date DESC
    ''')
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

def get_results_by_file(file_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM files WHERE id = ?', (file_id,))
    file_row = cursor.fetchone()

    if not file_row:
        conn.close()
        return {'error': 'File not found'}

    cursor.execute(
        'SELECT * FROM findings WHERE file_id = ? ORDER BY severity',
        (file_id,)
    )
    findings = cursor.fetchall()
    conn.close()

    return {
        'file': dict(file_row),
        'findings': [dict(f) for f in findings]
    }

def get_all_findings():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT findings.*, files.filename, files.language
        FROM findings
        JOIN files ON findings.file_id = files.id
        ORDER BY
            CASE severity
                WHEN 'CRITICAL' THEN 0
                WHEN 'HIGH' THEN 1
                WHEN 'MEDIUM' THEN 2
                WHEN 'LOW' THEN 3
            END
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_file(file_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM findings WHERE file_id = ?', (file_id,))
    cursor.execute('DELETE FROM files WHERE id = ?', (file_id,))
    conn.commit()
    conn.close()