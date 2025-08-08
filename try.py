from datetime import datetime,timedelta
import time as t
import sqlite3
from prisoners.main_app import CALCULATE_NEXT_DAY

db_path = "Z:/db/visit_report.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT date FROM holidays")
date_db = cursor.fetchall()

conn.close()

def cal_time():
    thai_days = ['จันทร์', 'อังคาร', 'พุธ', 'พฤหัสบดี', 'ศุกร์', 'เสาร์', 'อาทิตย์']
    today_str = "2025-08-22"  # หรือใช้ datetime.today().strftime("%Y-%m-%d")
    today_obj = datetime.strptime(today_str, "%Y-%m-%d")
    next_day_obj = today_obj + timedelta(days=1)

    while any(value[0] == next_day_obj.strftime("%Y-%m-%d") for value in date_db):
        next_day_obj += timedelta(days=1)

    weekday_thai = thai_days[next_day_obj.weekday()]
    return f"{weekday_thai}"


cal_next_day = CALCULATE_NEXT_DAY()
next_day = cal_next_day.get_next_day()
print(next_day)
if isinstance(next_day,datetime):
    next_day = next_day.strftime("%Y-%m-%d")
print(next_day)