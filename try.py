import os
import json
import sqlite3
import hashlib
from datetime import datetime

def get_config_path():
    return os.path.join(os.getcwd(), "config", "config.json")

def load_config():
    config_path = get_config_path()
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f).get('db_path')
    return ''

def create_users_table():
    """สร้างตาราง users ในฐานข้อมูล"""
    db_path = load_config()
    
    if not db_path or not os.path.exists(db_path):
        print("ไม่พบไฟล์ฐานข้อมูล กรุณาเลือกฐานข้อมูลก่อน")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # สร้างตาราง users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                fullname TEXT NOT NULL,
                user_type TEXT NOT NULL
            )
        ''')
        
        # เพิ่มข้อมูลเริ่มต้น
        default_users = [
            ('admin', '123456', 'กิติชัย ว่องไว','ADMIN'),
            ('user', '123456', 'ผู้ใช้ทั่วไป','USER')
        ]

        for username,password,fullname,user_type in default_users:
            cursor.execute('''
                INSERT INTO users (username, password, fullname, user_type)
                VALUES (?, ?, ?, ?)
            ''', (username, password, fullname, user_type))
            print(f"เพิ่มผู้ใช้: {username}")

        conn.commit()
        conn.close()
        
        print("✅ สร้างตาราง users เรียบร้อยแล้ว")
        print(f"📍 ฐานข้อมูล: {db_path}")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

def view_users():
    """แสดงรายการผู้ใช้ทั้งหมด"""
    db_path = load_config()
    
    if not db_path or not os.path.exists(db_path):
        print("ไม่พบไฟล์ฐานข้อมูล")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, username, fullname FROM users ORDER BY id')
        users = cursor.fetchall()
        
        if users:
            print("\n" + "="*50)
            print("รายการผู้ใช้ในระบบ")
            print("="*50)
            print(f"{'ID':<5} {'Username':<15} {'Fullname'}")
            print("-"*50)
            for user in users:
                print(f"{user[0]:<5} {user[1]:<15} {user[2]}")
            print("="*50)
        else:
            print("ไม่พบข้อมูลผู้ใช้")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    print("🔧 เครื่องมือจัดการตาราง Users")
    print("1. สร้างตารางและเพิ่มข้อมูลเริ่มต้น")
    print("2. ดูรายการผู้ใช้")
    print("3. เพิ่มผู้ใช้ใหม่")
    
    choice = input("\nเลือกเมนู (1-3): ")
    
    if choice == "1":
        create_users_table()
    elif choice == "2":
        view_users()
    else:
        print("❌ เลือกเมนูไม่ถูกต้อง")