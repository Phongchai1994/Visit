import pandas as pd
import sqlite3

def insert_data():
    # อ่านข้อมูลจาก Excel
    df = pd.read_excel("manage/prisoner_data.xlsx")

    # เชื่อมต่อกับ SQLite
    conn = sqlite3.connect("manage/visit_report.db")
    cursor = conn.cursor()

    # สร้างตาราง prisoners ถ้ายังไม่มี
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prisoners (
            prisoner_id INTEGER PRIMARY KEY,
            sex TEXT,
            f_name TEXT,
            l_name TEXT,
            lawsuit TEXT,
            level TEXT,
            dan TEXT,
            type TEXT,
            status TEXT
        )
    ''')

    # อ่าน prisoner_id ที่มีอยู่แล้วในฐานข้อมูล
    existing_ids = pd.read_sql_query("SELECT prisoner_id FROM prisoners", conn)
    existing_ids_set = set(existing_ids["prisoner_id"].tolist())

    # กรองเฉพาะแถวที่ prisoner_id ยังไม่อยู่ในฐานข้อมูล
    new_rows = df[~df["prisoner_id"].isin(existing_ids_set)]

    # เพิ่มเฉพาะแถวใหม่ลงในฐานข้อมูล
    new_rows.to_sql("prisoners", conn, if_exists="append", index=False)

    # ปิดการเชื่อมต่อ
    conn.close()
    print('อัพโหลดเสร็จ')

def update_data():
    # อ่านข้อมูลจาก Excel
    df = pd.read_excel("manage/prisoner_data.xlsx")

    # เพิ่มคอลัมน์ type และ status หากยังไม่มี
    for col in ['type', 'status']:
        if col not in df.columns:
            df[col] = None  # หรือ default value

    # เชื่อมต่อกับ SQLite
    conn = sqlite3.connect("manage/visit_report.db")
    cursor = conn.cursor()

    # สร้างตาราง prisoners ถ้ายังไม่มี
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prisoners (
            prisoner_id INTEGER PRIMARY KEY,
            sex TEXT,
            f_name TEXT,
            l_name TEXT,
            lawsuit TEXT,
            level TEXT,
            dan TEXT,
            type TEXT,
            status TEXT
        )
    ''')

    # อ่าน prisoner_id ที่มีอยู่แล้วในฐานข้อมูล
    existing_ids = pd.read_sql_query("SELECT prisoner_id FROM prisoners", conn)
    existing_ids_set = set(existing_ids["prisoner_id"].tolist())

    # --- เพิ่มข้อมูลใหม่ (ยังไม่มีใน DB) ---
    new_rows = df[~df["prisoner_id"].isin(existing_ids_set)]
    new_rows.to_sql("prisoners", conn, if_exists="append", index=False)

    # --- อัปเดตข้อมูล type และ status สำหรับ prisoner_id ที่มีอยู่แล้ว ---
    update_rows = df[df["prisoner_id"].isin(existing_ids_set)]

    for _, row in update_rows.iterrows():
        cursor.execute("""
            UPDATE prisoners
            SET type = ?, status = ?
            WHERE prisoner_id = ?
        """, (row["type"], row["status"], row["prisoner_id"]))

    # บันทึกการเปลี่ยนแปลง
    conn.commit()

    # ปิดการเชื่อมต่อ
    conn.close()
    print('แก้ไขเสร็จ')


update_data()