# ระบบเยี่ยมญาติผู้ต้องขัง

ระบบจองเยี่ยมญาติโดยการสแกนลายนิ้วมือและอ่านบัตรประชาชน

## คุณสมบัติหลัก
- 📋 ลงทะเบียนผู้ต้องขัง
- 🔍 ค้นหาและจัดการข้อมูลผู้ต้องขัง  
- 📅 ระบบจองเยี่ยมญาติ
- 👆 สแกนลายนิ้วมือ (ZK Fingerprint Scanner)
- 💳 อ่านบัตรประชาชน (Smart Card Reader)
- 📊 รายงานการเยี่ยมรายวันและรายเดือน
- 🔐 เข้ารหัสฐานข้อมูล
- 📄 สร้างไฟล์ PDF รายงาน

## การติดตั้ง

### ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### รันโปรแกรม
```bash
python main.py
```

## ไฟล์สำคัญ
- `main.py` - ไฟล์หลักสำหรับเรียกใช้โปรแกรม
- `requirements.txt` - รายการ dependencies
- `INSTALL.md` - คู่มือการติดตั้งแบบละเอียด
- `config/config.json` - ไฟล์ตั้งค่าระบบ

## โครงสร้างโปรเจค
```
Visit/
├── main.py                 # ไฟล์หลัก
├── requirements.txt        # Dependencies
├── user_session.py         # จัดการ session ผู้ใช้
├── prisoners/              # โมดูลหลัก
│   ├── main_app.py        # หน้าหลักของแอป
│   ├── menu_app.py        # เมนูของแอป
│   └── card_reader.py     # อ่านบัตรประชาชน
├── manage/                 # จัดการระบบ
│   ├── database.py        # ฐานข้อมูล
│   ├── encryption_utils.py # เข้ารหัส
│   └── excel_to_db.py     # นำเข้า Excel
└── config/                 # ไฟล์ตั้งค่า
    └── config.json
```

## ข้อกำหนดระบบ
- Python 3.8+
- Windows 10/11  
- เครื่องอ่านบัตรประชาชน (Smart Card Reader)
- เครื่องสแกนลายนิ้วมือ (ZK Fingerprint Scanner)
