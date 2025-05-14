import pandas as pd
import sqlite3

# อ่านข้อมูลจาก Excel
df = pd.read_excel("prisoners.xlsx")

# เชื่อมต่อกับ SQLite (สร้างไฟล์ฐานข้อมูลถ้ายังไม่มี)
conn = sqlite3.connect("prison.db")
cursor = conn.cursor()

# สร้างตาราง prisoners (กำหนดชนิดข้อมูลให้เหมาะสม)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS prisoners (
        prisoner_id INTEGER PRIMARY KEY,
        sex TEXT,
        f_name TEXT,
        l_name TEXT,
        lawsuit TEXT,
        level TEXT,
        dan TEXT
    )
''')

# เพิ่มข้อมูลลงในตาราง (append)
df.to_sql("prisoners", conn, if_exists="append", index=False)

# ปิดการเชื่อมต่อ
conn.close()
