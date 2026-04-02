"""
Module สำหรับจัดการ User Session
สามารถ import ใช้ได้จากไฟล์อื่น ๆ
"""
import datetime
from tkinter import messagebox

class UserSession:
    def __init__(self):
        self.is_logged_in = False
        self.user_id = None
        self.username = None
        self.fullname = None  # เพิ่มฟิลด์ fullname
        self.user_type = None
        self.login_time = None
    
    def login(self, username, user_type, user_id=None, fullname=None):
        """เข้าสู่ระบบ"""
        self.is_logged_in = True
        self.user_id = user_id
        self.username = username
        self.fullname = fullname or username  # ใช้ username เป็นค่าเริ่มต้น
        self.user_type = user_type
        self.login_time = datetime.datetime.now()
        print(f"User {self.fullname} ({self.username}) logged in as {self.user_type}")
    
    
    def logout(self):
        """ออกจากระบบ"""
        self.is_logged_in = False
        self.user_type = None
        self.username = None
        self.login_time = None
    
    def is_admin(self):
        """ตรวจสอบว่าเป็น admin หรือไม่"""
        return self.user_type == 'admin'
    
    def is_user(self):
        """ตรวจสอบว่าเป็น user หรือไม่"""
        return self.user_type == 'user'
    
    def is_visit(self):
        return self.user_type == 'visit'
    
    def get_user_info(self):
        """ได้ข้อมูลผู้ใช้ในรูปแบบ dict"""
        return {
            'username': self.username,
            'user_type': self.user_type,
            'is_logged_in': self.is_logged_in,
            'login_time': self.login_time
        }

# สร้าง instance global
user_session = UserSession()

# Decorator functions
def require_admin(func):
    """Decorator สำหรับตรวจสอบสิทธิ์ admin"""
    def wrapper(*args, **kwargs):
        if not user_session.is_admin():
            messagebox.showerror("ไม่มีสิทธิ์", "เฉพาะผู้ดูแลระบบเท่านั้นที่สามารถใช้ฟีเจอร์นี้ได้")
            return None
        return func(*args, **kwargs)
    return wrapper

def require_login(func):
    """Decorator สำหรับตรวจสอบการเข้าสู่ระบบ"""
    def wrapper(*args, **kwargs):
        if not user_session.is_logged_in:
            messagebox.showerror("ไม่ได้เข้าสู่ระบบ", "กรุณาเข้าสู่ระบบก่อนใช้ฟีเจอร์นี้")
            return None
        return func(*args, **kwargs)
    return wrapper
