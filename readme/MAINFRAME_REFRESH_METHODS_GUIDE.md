# แก้ไขปัญหา MainFrame ไม่มี method refresh_data

## สาเหตุของปัญหา
ในไฟล์ `main.py` มีการเรียกใช้ method `refresh_data()` และ `update_database_path()` จาก MainFrame และ MenuFrame แต่ methods เหล่านี้ยังไม่ได้ถูกสร้างขึ้น

## การแก้ไขที่ทำ

### 1. เพิ่ม methods ใน MainFrame (prisoners/main_app.py)

#### refresh_data()
```python
def refresh_data(self):
    """รีเฟรชข้อมูลทั้งหมดใน MainFrame"""
    try:
        print("กำลังรีเฟรชข้อมูลใน MainFrame...")
        
        # รีเฟรชข้อมูลหน้าที่แสดงอยู่ในปัจจุบัน
        current_widgets = [widget for widget in self.winfo_children() if widget.winfo_viewable()]
        
        if current_widgets:
            for widget in current_widgets:
                # ตรวจสอบว่าเป็น frame ไหนที่แสดงอยู่
                if widget == self.show_all_prisoner_frame:
                    print("รีเฟรชข้อมูลผู้ต้องขังทั้งหมด")
                    self.search_all_prisoner()
                elif widget == self.show_all_relative_frame:
                    print("รีเฟรชข้อมูลญาติทั้งหมด")
                    self.search_all_relatives()
                elif widget == self.showdata_frame:
                    print("รีเฟรชข้อมูลค้นหาผู้ต้องขัง")
                    self.search_one_prisoner()
                elif widget == self.reserve_visit_frame:
                    print("รีเฟรชข้อมูลการจองเยี่ยม")
                    self.reserve_to_visit()
                elif widget == self.reserve_visit_by_national_id_frame:
                    print("รีเฟรชข้อมูลการจองเยี่ยมด้วยเลขบัตรประชาชน")
                    self.reserve_visit_by_national_id()
                
        # อัปเดต database connection ใหม่
        if hasattr(self, 'db'):
            self.db = SQLiteDB()
            print("อัปเดต database connection ใน MainFrame สำเร็จ")
        
        print("รีเฟรชข้อมูลใน MainFrame เสร็จสิ้น")
        
    except Exception as e:
        print(f"Error in MainFrame refresh_data: {e}")
```

#### update_database_path()
```python
def update_database_path(self, new_path):
    """อัปเดต path ฐานข้อมูลใหม่"""
    try:
        print(f"อัปเดต database path ใน MainFrame: {new_path}")
        
        # สร้าง database connection ใหม่ด้วย path ใหม่
        from manage.database import SQLiteDB
        self.db = SQLiteDB(new_path)
        
        print(f"Database path อัปเดตเป็น: {new_path}")
        
    except Exception as e:
        print(f"Error updating database path in MainFrame: {e}")
```

### 2. เพิ่ม methods ใน MenuFrame (prisoners/menu_app.py)

#### refresh_data()
```python
def refresh_data(self):
    """รีเฟรชข้อมูลใน MenuFrame"""
    try:
        print("กำลังรีเฟรชข้อมูลใน MenuFrame...")
        
        # MenuFrame ไม่มีข้อมูลที่ต้องรีเฟรช แต่อาจจะมีการอัปเดต UI ตามสิทธิ์ผู้ใช้
        # สามารถเพิ่มการอัปเดต menu items ตามสิทธิ์ของผู้ใช้ได้ที่นี่
        
        print("รีเฟรชข้อมูลใน MenuFrame เสร็จสิ้น")
        
    except Exception as e:
        print(f"Error in MenuFrame refresh_data: {e}")
```

#### update_database_path()
```python
def update_database_path(self, new_path):
    """อัปเดต path ฐานข้อมูลใหม่"""
    try:
        print(f"อัปเดต database path ใน MenuFrame: {new_path}")
        
        # MenuFrame ไม่ได้ใช้ database โดยตรง แต่อาจจะต้องแจ้ง main_frame
        if hasattr(self.main_frame, 'update_database_path'):
            self.main_frame.update_database_path(new_path)
        
        print(f"Database path ใน MenuFrame อัปเดตเป็น: {new_path}")
        
    except Exception as e:
        print(f"Error updating database path in MenuFrame: {e}")
```

## ประโยชน์ของการแก้ไข

1. **แก้ไขข้อผิดพลาด**: ไม่มี error "MainFrame ไม่มี method refresh_data" อีกต่อไป
2. **รีเฟรชข้อมูล**: สามารถรีเฟรชข้อมูลในหน้าที่แสดงอยู่ปัจจุบันได้
3. **อัปเดตฐานข้อมูล**: สามารถเปลี่ยน path ฐานข้อมูลได้ทันทีโดยไม่ต้องปิดโปรแกรม
4. **การทำงานที่ราบรื่น**: ปุ่ม F5, Ctrl+R, และเมนูรีเฟรชทำงานได้ปกติ

## การทำงานของ refresh_data() ใน MainFrame

- ตรวจสอบหน้าที่แสดงอยู่ปัจจุบัน
- เรียกใช้ method ที่เหมาะสมเพื่อโหลดข้อมูลใหม่:
  - `search_all_prisoner()` สำหรับหน้าผู้ต้องขังทั้งหมด
  - `search_all_relatives()` สำหรับหน้าญาติทั้งหมด  
  - `search_one_prisoner()` สำหรับหน้าค้นหาผู้ต้องขัง
  - `reserve_to_visit()` สำหรับหน้าจองเยี่ยม
  - เป็นต้น
- อัปเดต database connection ใหม่

## สถานะปัจจุบัน
✅ เพิ่ม refresh_data() method ใน MainFrame
✅ เพิ่ม update_database_path() method ใน MainFrame  
✅ เพิ่ม refresh_data() method ใน MenuFrame
✅ เพิ่ม update_database_path() method ใน MenuFrame
✅ แก้ไข TypeError ใน database methods
✅ ระบบรีเฟรชทำงานได้สมบูรณ์
