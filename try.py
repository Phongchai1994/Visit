from datetime import datetime,timedelta
# import time as t
# import sqlite3
# from prisoners.main_app import CALCULATE_NEXT_DAY
# from manage.database import SQLiteDB
# # import hashlib

# db = SQLiteDB()

# db_path = "C:/Users/ADMINS/Visit-Turnstile/utility/visit_report.db"
# conn = db.connect(db_path)
# cursor = conn.cursor()


# username = "user_visit"
# password = "066986"  # ต้องเป็น string

# password_blob = hashlib.sha256(password.encode("utf-8")).digest()  # bytes = BLOB


# cursor.execute(
#     "INSERT INTO users (username, password, user_type, fullname) VALUES (?, ?, ?, ?)",
#     (username, password_blob, "visit", "สำหรับจองเยี่ยม")
# )

# conn.commit()
# conn.close()

# def get_chanel_blank_on_visit_spacial(time,date):
#     cursor.execute('SELECT channel FROM visit_spacial WHERE date_visit = ? AND time_visit = ?',(date,time))
#     data = [row[0] for row in cursor.fetchall() if row[0] is not None]
#     # print(f'data = {data}')
#     return data
    

# def get_distinct():
#     cursor.execute("SELECT DISTINCT strftime('%Y', date_visit) FROM visit_spacial ORDER BY 1")
#     years = [row[0] for row in cursor.fetchall()]
#     cursor.execute("SELECT DISTINCT strftime('%m', date_visit) FROM visit_spacial ORDER BY 1")
#     months = [row[0] for row in cursor.fetchall()]
#     cursor.execute("SELECT DISTINCT strftime('%d', date_visit) FROM visit_spacial ORDER BY 1")
#     days = [row[0] for row in cursor.fetchall()]
#     return {'years': years, 'months': months, 'days': days}

# # print(get_distinct())

# # distinct = db.get_date_on_visit_spacial()
# # print(distinct)

# now = datetime.now().time()
# print(now)


# from escpos.printer import Usb
# from PIL import Image

# VENDOR_ID = 0x04b8
# PRODUCT_ID = 0x0e27

# printer = Usb(VENDOR_ID, PRODUCT_ID)
# printer.profile.media['width']['pixels'] = 576
# print(printer.profile.media)
# logo = Image.open('logo.png')
# logo = logo.resize((200,200))
# logo = logo.convert('1')

# printer.set(align='center')
# printer.image(logo)
# printer.set(width=1, height=1)
# printer.text("ข้อความขนาดปกติ\n")

# # ขนาดใหญ่ขึ้น 2 เท่า
# printer.set(width=2, height=2)
# printer.text("ข้อความขนาดใหญ่\n")

# # กลับไปขนาดปกติ
# printer.set(width=1, height=1)
# printer.cut()


today_now = datetime.today().date().isoformat()
month_now = today_now[:7]
date = "2025-05-04"
print(today_now)