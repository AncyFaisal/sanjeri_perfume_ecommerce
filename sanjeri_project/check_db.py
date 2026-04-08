import sqlite3
import os

try:
    print("File exists:", os.path.exists('db.sqlite3'))
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(sanjeri_app_customuser)")
    columns = cursor.fetchall()
    print("Found columns:", len(columns))
    for col in columns:
        print(col)
    conn.close()
except Exception as e:
    print(f"Error: {e}")
