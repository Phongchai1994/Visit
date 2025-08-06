# คู่มือการใช้งาน User Session System

## 🔐 ระบบจัดการสิทธิ์ผู้ใช้

### บัญชีผู้ใช้ทดสอบ:
```
admin/123456    - สิทธิ์ Admin
user/123456     - สิทธิ์ User
manager/123456  - สิทธิ์ Admin
staff/123456    - สิทธิ์ User
```

## 📁 ไฟล์ที่เกี่ยวข้อง:
- `user_session.py` - Module หลักสำหรับจัดการ session
- `main.py` - แก้ไขเพิ่มระบบ login และ session
- `example_menu_app_usage.py` - ตัวอย่างการใช้ใน menu_app.py
- `example_main_app_usage.py` - ตัวอย่างการใช้ใน main_app.py

## 🚀 วิธีใช้งานใน menu_app.py และ main_app.py:

### 1. Import module:
```python
from user_session import user_session, require_admin, require_login
```

### 2. ตรวจสอบสิทธิ์:
```python
# ตรวจสอบว่าเป็น admin หรือไม่
if user_session.is_admin():
    # ทำงานเฉพาะ admin
    pass

# ตรวจสอบว่าเป็น user หรือไม่
if user_session.is_user():
    # ทำงานเฉพาะ user
    pass

# ตรวจสอบว่าเข้าสู่ระบบแล้วหรือไม่
if user_session.is_logged_in:
    # ทำงานเมื่อเข้าสู่ระบบแล้ว
    pass
```

### 3. ใช้ Decorators:
```python
@require_admin
def admin_only_function():
    """ฟังก์ชันเฉพาะ admin"""
    pass

@require_login
def login_required_function():
    """ฟังก์ชันต้องเข้าสู่ระบบ"""
    pass
```

### 4. ข้อมูลผู้ใช้:
```python
username = user_session.username
user_type = user_session.user_type
login_time = user_session.login_time
```

## 🎯 ฟีเจอร์หลัก:

### ✅ ที่เพิ่มใน main.py:
- หัวข้อแสดงชื่อผู้ใช้และสิทธิ์
- เมนู "ผู้ดูแลระบบ" สำหรับ admin เท่านั้น
- เมนู "ออกจากระบบ"
- Status bar แสดงข้อมูลผู้ใช้
- ตรวจสอบสิทธิ์ก่อนเลือกฐานข้อมูล
- ระบบ login หลายบัญชี

### ✅ การใช้งานใน menu_app.py:
- สร้างเมนูตามสิทธิ์ผู้ใช้
- แสดงข้อมูลผู้ใช้ในเมนู
- ตรวจสอบสิทธิ์ก่อนเรียกฟังก์ชัน

### ✅ การใช้งานใน main_app.py:
- สร้าง UI ตามสิทธิ์ผู้ใช้
- ตรวจสอบสิทธิ์สำหรับฟีเจอร์ต่างๆ
- แสดง/ซ่อนปุ่มตามสิทธิ์

## 🔧 ตัวอย่างการใช้งานจริง:

### ใน prisoners/menu_app.py:
```python
from user_session import user_session, require_admin, require_login

class MenuFrame:
    def __init__(self, parent, main_frame):
        self.parent = parent
        self.main_frame = main_frame
        
        # สร้างเมนูตามสิทธิ์
        self.create_menu()
    
    def create_menu(self):
        if user_session.is_admin():
            # เมนูเฉพาะ admin
            self.create_admin_buttons()
        
        # เมนูทั่วไป
        self.create_common_buttons()
```

### ใน prisoners/main_app.py:
```python
from user_session import user_session, require_admin, require_login

class MainFrame:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        if user_session.is_admin():
            # แสดงปุ่มลบข้อมูล
            self.create_delete_button()
        
        # แสดงข้อมูลผู้ใช้
        self.show_user_info()
    
    @require_admin
    def delete_record(self):
        # ลบข้อมูล (เฉพาะ admin)
        pass
```

## 🛡️ ความปลอดภัย:
- ตรวจสอบสิทธิ์แบบ real-time
- Decorators ป้องกันการเรียกฟังก์ชันโดยไม่มีสิทธิ์
- Session management ที่ปลอดภัย
- แยกสิทธิ์ admin และ user อย่างชัดเจน

## 📝 หมายเหตุ:
- ไม่กระทบต่อโครงสร้างเดิมของโปรแกรม
- สามารถใช้ได้ทุกไฟล์เพียงแค่ import
- ข้อมูล login ควรเก็บในฐานข้อมูลและเข้ารหัสในการใช้งานจริง
