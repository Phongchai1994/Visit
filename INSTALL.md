# ระบบเยี่ยมญาติผู้ต้องขัง - คู่มือการติดตั้ง

## ข้อกำหนดระบบ
- Python 3.8+ 
- Windows 10/11
- เครื่องอ่านบัตรประชาชน (Smart Card Reader)
- เครื่องสแกนลายนิ้วมือ (ZK Fingerprint Scanner)

## การติดตั้ง Dependencies

### วิธีที่ 1: ติดตั้งจาก requirements.txt
```bash
pip install -r requirements.txt
```

### วิธีที่ 2: ติดตั้งแบบง่าย
```bash
pip install -r requirements-simple.txt
```

### วิธีที่ 3: ติดตั้งทีละตัว
```bash
pip install customtkinter>=5.2.0
pip install cryptography>=41.0.0
pip install reportlab>=4.0.0
pip install pandas>=2.0.0
pip install pyscard>=2.0.0
pip install pyzkfp>=1.0.0
pip install emoji>=2.8.0
```

## การรันโปรแกรม
```bash
python main.py
```

## หมายเหตุสำคัญ
1. **customtkinter**: สำหรับ UI ที่ทันสมัย
2. **cryptography**: สำหรับเข้ารหัสฐานข้อมูล
3. **reportlab**: สำหรับสร้างไฟล์ PDF รายงาน
4. **pandas**: สำหรับจัดการข้อมูล Excel
5. **pyscard**: สำหรับอ่านบัตรประชาชน
6. **pyzkfp**: สำหรับเครื่องสแกนลายนิ้วมือ ZK
7. **emoji**: สำหรับแสดง emoji ใน UI

## การแก้ไขปัญหาการติดตั้ง

### หาก pyscard ติดตั้งไม่ได้:
```bash
# สำหรับ Windows
pip install pyscard --upgrade --force-reinstall
# หรือ
conda install pyscard
```

### หาก pyzkfp ติดตั้งไม่ได้:
```bash
# อาจต้องติดตั้ง Microsoft Visual C++ Build Tools
# หรือใช้ wheel file ที่รวบรวมแล้ว
pip install pyzkfp --find-links https://pypi.org/simple/
```

### หาก reportlab มีปัญหากับ Thai fonts:
- ตรวจสอบให้แน่ใจว่ามี TH SarabunPSK font ในระบบ
- หรือใส่ไฟล์ font ในโฟลเดอร์ fonts/ ของโปรเจค
