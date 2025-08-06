# คู่มือการอัปเดตฐานข้อมูลแบบ Real-time

## 🔄 ฟีเจอร์ใหม่ที่เพิ่มเข้าไป:

### ✅ การเลือกฐานข้อมูลใหม่ (ใน main.py):
- ตรวจสอบสิทธิ์ admin ก่อนให้เลือกฐานข้อมูล
- อัปเดต path ฐานข้อมูลทันทีโดยไม่ต้องปิดโปรแกรม
- รีเฟรชข้อมูลใน MainFrame และ MenuFrame อัตโนมัติ
- อัปเดต Status Bar แสดงชื่อฐานข้อมูลปัจจุบัน

### ✅ ฟังก์ชันหลักที่เพิ่มใน App_Prisoners:

1. **`refresh_database_connection()`** - รีเฟรชการเชื่อมต่อฐานข้อมูล
2. **`update_status_bar()`** - อัปเดต Status Bar
3. **Status Bar ใหม่** - แสดงชื่อไฟล์ฐานข้อมูลปัจจุบัน

## 🔧 การปรับใช้ใน MainFrame และ MenuFrame:

### ใน prisoners/main_app.py เพิ่ม:
```python
def update_database_path(self, new_path):
    """อัปเดต path ฐานข้อมูลใหม่"""
    self.db_path = new_path
    self.refresh_data()

def refresh_data(self):
    """รีเฟรชข้อมูลจากฐานข้อมูลใหม่"""
    # โหลดข้อมูลใหม่จากฐานข้อมูล
    self.load_prisoners_data()
    self.load_visits_data()
    self.update_display()
```

### ใน prisoners/menu_app.py เพิ่ม:
```python
def update_database_path(self, new_path):
    """อัปเดต path ฐานข้อมูลใหม่"""
    self.db_path = new_path
    self.update_menu_states()

def update_menu_states(self):
    """เปิด/ปิดปุ่มตาม path ฐานข้อมูล"""
    if self.db_path:
        self.enable_database_dependent_buttons()
    else:
        self.disable_database_dependent_buttons()
```

## 🚀 การทำงาน:

### เมื่อเลือกฐานข้อมูลใหม่:
1. ✅ ตรวจสอบสิทธิ์ admin
2. ✅ เลือกไฟล์ฐานข้อมูล
3. ✅ บันทึก path ลงไฟล์ config
4. ✅ อัปเดต `self.db_path`
5. ✅ เรียก `refresh_database_connection()`
6. ✅ อัปเดต MainFrame และ MenuFrame
7. ✅ รีเฟรช Status Bar
8. ✅ แสดงข้อความยืนยัน

### Status Bar จะแสดง:
```
ผู้ใช้: admin | สิทธิ์: ADMIN | เข้าสู่ระบบ: 07/08/2025 14:30 | ฐานข้อมูล: visit_report.db
```

## 💡 ประโยชน์:
- **ไม่ต้องปิดโปรแกรม** - เปลี่ยนฐานข้อมูลได้ทันที
- **อัปเดตอัตโนมัติ** - ข้อมูลทุกส่วนอัปเดตทันที
- **ปลอดภัย** - เฉพาะ admin เท่านั้นที่เปลี่ยนได้
- **แสดงสถานะ** - เห็นฐานข้อมูลปัจจุบันใน Status Bar
- **การจัดการข้อผิดพลาด** - มีการจัดการ error อย่างเหมาะสม

## 🔒 ความปลอดภัย:
- ตรวจสอบสิทธิ์ admin ก่อนเลือกฐานข้อมูล
- จัดการ exception เมื่อเกิดข้อผิดพลาด
- บันทึก log การเปลี่ยนแปลงฐานข้อมูล
