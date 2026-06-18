import os
import sys
from dotenv import load_dotenv

def get_project_root():
    if getattr(sys, 'frozen', False):
        # 1. ตอนเป็น .exe
        # คืนค่าตำแหน่งโฟลเดอร์ที่ไฟล์ .exe วางตัวอยู่ปัจจุบัน
        return os.path.dirname(sys.executable)
    else:
        # 2. ตอนเป็น .py ปกติ
        # os.path.dirname(__file__) จะได้ Path ของโฟลเดอร์ visit/manage
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # ใช้ '..' เพื่อถอยหลังออกไป 1 ชั้น จะได้ Path ของโฟลเดอร์หลักคือ visit/
        return os.path.abspath(os.path.join(current_dir, '..'))

def load_project_env():
    root_dir = get_project_root()
    
    # จากโฟลเดอร์หลัก (visit/) ให้เดินหน้าเข้าโฟลเดอร์ config แล้วชี้ไปที่ไฟล์ .env
    env_path = os.path.join(root_dir, 'config', '.env')
    
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"Loaded .env จาก: {env_path}")
    else:
        print(f"Warning: ไม่พบไฟล์ .env ที่ตำแหน่ง {env_path}")

# สั่งให้โหลด env ทันทีเมื่อมีการ import ไฟล์นี้ไปใช้งาน
load_project_env()