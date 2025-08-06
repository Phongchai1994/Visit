# แก้ไขปัญหาต้องปิด-เปิดโปรแกรมใหม่เพื่อเข้าถึงฐานข้อมูล

## สาเหตุของปัญหา
เมื่อเปลี่ยน path ฐานข้อมูลใหม่ แต่ database instances ที่สร้างไว้แล้วยังคงใช้ path เดิม ทำให้ต้องปิดโปรแกรมและเปิดใหม่เพื่อให้โหลด config ใหม่

## การแก้ไขที่ทำ

### 1. แก้ไข SQLiteDB Constructor (manage/database.py)

**ปัญหาเดิม:**
```python
def __init__(self, db_path=load_config()):
```
- `load_config()` ถูกเรียกแค่ครั้งเดียวตอน import module
- ไม่ได้โหลด config ใหม่เมื่อสร้าง instance ใหม่

**การแก้ไข:**
```python
def __init__(self, db_path=None):
    # โหลด path จาก config ทุกครั้งที่สร้าง instance ใหม่
    if db_path is None:
        db_path = load_config()
    self.db_path = db_path
    self.conn = None
    self.cursor = None
```

### 2. ปรับปรุง update_database_path ใน MainFrame

**เพิ่มการปิด connection เดิม:**
```python
def update_database_path(self, new_path):
    try:
        # ปิด connection เดิมก่อน (ถ้ามี)
        if hasattr(self, 'db') and self.db:
            try:
                self.db.close()
            except:
                pass
        
        # สร้าง database connection ใหม่ด้วย path ใหม่
        from manage.database import SQLiteDB
        self.db = SQLiteDB(new_path)
        
        # ทดสอบการเชื่อมต่อ
        test_connection = self.db.connect()
        if test_connection:
            print(f"Database connection ใหม่สำเร็จ: {new_path}")
        else:
            print(f"Database connection ล้มเหลว: {new_path}")
            
    except Exception as e:
        print(f"Error updating database path in MainFrame: {e}")
```

### 3. ปรับปรุง refresh_data ใน MainFrame

**เพิ่มการ reload database connection:**
```python
# อัปเดต database connection ใหม่
if hasattr(self, 'db'):
    # ปิด connection เดิมก่อน
    try:
        self.db.close()
    except:
        pass
    # สร้าง instance ใหม่เพื่อโหลด config ล่าสุด
    from manage.database import SQLiteDB
    self.db = SQLiteDB()
    print("อัปเดต database connection ใน MainFrame สำเร็จ")
```

### 4. เพิ่ม Force Reload ใน main.py

**ใน select_database method:**
```python
if file_path:
    # อัปเดต path ฐานข้อมูลใหม่
    self.db_path = file_path
    save_config(file_path)
    
    # Force reload database path ใน modules
    import importlib
    import manage.database
    importlib.reload(manage.database)
    
    # อัปเดตข้อมูลใน main_frame และ menu_frame
    self.refresh_database_connection()
    
    # รีเฟรชข้อมูลทั้งหมด
    self.refresh_all_data()
```

### 5. ปรับปรุง refresh_database_connection

**เพิ่มการตรวจสอบ config path:**
```python
def refresh_database_connection(self):
    try:
        # Force reload config ให้แน่ใจว่าได้ path ใหม่
        from manage.database import load_config
        current_path = load_config()
        print(f"Current config path: {current_path}")
        print(f"New path: {self.db_path}")
        
        # อัปเดต path ให้กับ main_frame และ menu_frame
        # รีเฟรชข้อมูลทั้งหมด
        # อัปเดต status bar
    except Exception as e:
        # จัดการ error
```

## วิธีการทำงานหลังแก้ไข

1. **เลือกฐานข้อมูลใหม่** → บันทึก config → Force reload modules
2. **อัปเดต database instances** → ปิด connection เดิม → สร้าง instance ใหม่ 
3. **ทดสอบการเชื่อมต่อ** → ตรวจสอบว่าใช้ path ใหม่ได้
4. **รีเฟรชข้อมูล** → โหลดข้อมูลจากฐานข้อมูลใหม่
5. **อัปเดต UI** → แสดงข้อมูลใหม่ทันที

## ประโยชน์ที่ได้รับ

✅ **ไม่ต้องปิด-เปิดโปรแกรม** - เปลี่ยนฐานข้อมูลได้ทันที
✅ **Connection ถูกต้อง** - ใช้ path ใหม่ทันทีหลังเปลี่ยน
✅ **ข้อมูลล่าสุด** - แสดงข้อมูลจากฐานข้อมูลใหม่ทันที
✅ **Error Handling** - จัดการ error เมื่อไม่สามารถเชื่อมต่อได้
✅ **ความมั่นคง** - ปิด connection เดิมก่อนสร้างใหม่

## การทดสอบ

1. เปิดโปรแกรม → เลือกฐานข้อมูล A
2. ดูข้อมูลในฐานข้อมูล A 
3. เปลี่ยนเป็นฐานข้อมูล B โดยไม่ปิดโปรแกรม
4. ตรวจสอบว่าแสดงข้อมูลจากฐานข้อมูล B ทันที
5. ใช้ฟีเจอร์ต่างๆ เช่น ค้นหา, เพิ่มข้อมูล, แก้ไข
6. ตรวจสอบว่าทุกฟีเจอร์ทำงานกับฐานข้อมูลใหม่

## หมายเหตุ

- การแก้ไขนี้รองรับการเปลี่ยนฐานข้อมูลแบบ real-time
- ไม่ส่งผลกระทบต่อการทำงานปกติของโปรแกรม
- ยังคงรองรับการใช้งานหลายฐานข้อมูล
- มีการจัดการ error อย่างเหมาะสม
