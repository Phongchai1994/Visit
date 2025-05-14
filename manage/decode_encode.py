from cryptography.fernet import Fernet
import set_key
import os
import json
from pathlib import Path
import tempfile
import time
import sqlite3
import pandas as pd


TEMP_DIR = Path(tempfile.gettempdir()) # สร้างไฟล์ชั่วคราวไว้ใน Temp

def get_config_path():
    return os.path.join(os.getcwd(), "config", "config.json")

def load_config():
    config_path = get_config_path()
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f).get('db_path')
    return ''

def save_config(file_path):
    config_path = get_config_path()
    os.makedirs(os.path.dirname(config_path), exist_ok=True)  # ✅ สร้างโฟลเดอร์ถ้ายังไม่มี
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump({'db_path': file_path}, f)

TEMP_DIR = Path(tempfile.gettempdir())
EN_DB = load_config()
DE_DB = TEMP_DIR / 'visit_report.db'

def decrypt_file_onetime(input_file,output_file):
    key = set_key.load_key()
    f = Fernet(key)

    with open(input_file,'rb') as f_in:
        encrypted_data = f_in.read()
        
    decrypted = f.decrypt(encrypted_data)
    
    with open(output_file,'wb') as f_out:
        f_out.write(decrypted)
    print('Decode')

def encrypt_file_onetime(input_file, output_file):
    key = set_key.load_key()
    f = Fernet(key)

    with open(input_file, 'rb') as f_in:
        data = f_in.read()

    encrypted = f.encrypt(data)

    with open(output_file, 'wb') as f_out:
        f_out.write(encrypted)

    time.sleep(0.5)  # 🔧 รอให้ระบบปล่อยไฟล์ก่อนลบ

    try:
        os.remove(input_file)
        print('Encode and deleted original file')
    except Exception as e:
        print(f'Encode done, but failed to delete original file: {e}')

def insert_datas_to_db():
    db_path = DE_DB

    file_path = "prisoner_data.xlsx"
    sheet_name = "1"
    df = pd.read_excel(file_path,sheet_name=sheet_name,engine='openpyxl')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    sql = """
        INSERT INTO prisoners (prisoner_id,sex,f_name,l_name,lawsuit,level,dan)
        VALUES (?,?,?,?,?,?,?)
    """
    print(df.values.tolist())
    # cursor.executemany(sql,df.values.tolist())

    conn.close()
    encrypt_file_onetime(DE_DB,EN_DB)

insert_datas_to_db()
# decrypt_file_onetime(EN_DB,DE_DB)

# encrypt_file_onetime(DE_DB,EN_DB)