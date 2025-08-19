# import hashlib
# from manage.database import SQLiteDB
# user_password = hashlib.sha256(b'123456').digest()
# admin_password = hashlib.sha256(b'066986').digest()

# db = SQLiteDB()
# db.set_execute_manual('''INSERT INTO users (username ,password ,user_type ,fullname) VALUES (?,?,?,?)''', ('user', user_password, 'user', 'ผู้ใช้ทั่วไป'))

from datetime import datetime

today = datetime.today()
date_str = today.strftime("%Y-%m-%d")

print(f'date format = {date_str}')