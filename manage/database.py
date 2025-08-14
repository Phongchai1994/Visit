import sqlite3
import os
from manage.encryption_utils import decrypt_file,encrypt_file
from tkinter import messagebox
import json
from pathlib import Path
import tempfile


TEMP_DIR = Path(tempfile.gettempdir()) # สร้างไฟล์ชั่วคราวไว้ใน Temp


def get_config_path():
    return os.path.join(os.getcwd(), "config", "config.json")

def load_config():
    config_path = get_config_path()
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f).get('db_path')
    return ''

def check_key_on_db():
    db = sqlite3.connect(load_config())
    cursor = db.cursor()
    cursor.execute('SELECT key FROM check_')
    result = cursor.fetchone()
    db.close()
    return result[0] if result else None

def require_valid_key(func):
    KEY = 'E54F2JN5F2'
    KEY_DB = check_key_on_db()
    def wrapper(self, *args, **kwargs):
        if KEY_DB != KEY:
            raise PermissionError("KEY ไม่ถูกต้อง ไม่สามารถใช้งาน method นี้ได้")
        return func(self, *args, **kwargs)
    return wrapper

class SQLiteDB:
    def __init__(self, db_path=None):
        # โหลด path จาก config ทุกครั้งที่สร้าง instance ใหม่
        if db_path is None:
            db_path = load_config()
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.key = self.check_key()
        # โปรแกรมถอดรหัส และเข้ารหัส
        # self.EN_DB = load_config()  # โหลดข้อมูลจาก ไฟล์ config.json
        # self.DE_DB = TEMP_DIR / 'visit_report.db'

    def msgbox(self,e):
        messagebox.showerror('ฐานข้อมูล',f'{e}')

    def connect(self):
        try:
            if not self.db_path or not os.path.exists(self.db_path):
                print(f"Error: Database path is invalid or file doesn't exist: {self.db_path}")
                return False
                
            self.conn = sqlite3.connect(self.db_path)
            self.conn.execute('PRAGMA foreign_keys = ON')
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            messagebox.showerror('เชื่อมต่อฐานข้อมูลไม่สำเร็จ',str(e))
            self.conn = None
            self.cursor = None
            return False

        # print('เชื่อมต่อฐานข้อมูล')

    def close(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()
            self.conn = None
            self.cursor = None
            # print('ปิดฐานข้อมูล')
    def check_key(self):
        self.connect()
        try:
            self.cursor.execute('SELECT key FROM check_')
            return self.cursor.fetchone()[0]
        except Exception as e:
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาด : {e}')
            return False
        finally:
            self.close()

    # เพิ่มข้อมูลผู้ต้องขังใส่ตาราง prisoners
    @require_valid_key
    def add_data(self,data):
        self.connect()
        try :
            print('กำลังบันทึกข้อมูล')
            self.cursor.execute('INSERT INTO prisoners (prisoner_id,sex,f_name,l_name,lawsuit,level,dan,type,status) VALUES (?,?,?,?,?,?,?,?,?)',data)
            return True
        except Exception as e:
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาด : {e}')
            return False
        finally:
            self.close()

    # เพิ่มข้อมูลญาติใสในตาราง relatives
    @require_valid_key
    def add_data_ralative_to_relatives(self,id,data,relation):
        self.connect()
        try:
            # บันทึกข้อมูล ในตารางญาติ
            self.cursor.execute('INSERT INTO relatives (relative_id,title,f_name,l_name,address,tel) VALUES (?,?,?,?,?,?)',(data[0],data[1],data[2],data[3],data[4],data[5]))
            print('บันทึกข้อมูลตาราง relatives')
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            self.close()
            self.encode_db()

    # เพิมความสัมพันธ์ของญาติและผู้ต้องขังโดยใส่ในตาราง relations
    @require_valid_key
    def add_data_relation_to_ralations(self,id,data,relation):
        self.decode_db()
        self.connect()
        
        try:
            # บันทึกข้อมูลใน relation
            self.cursor.execute('INSERT INTO relations (prisoner_id,relative_id,relation) VALUES (?,?,?)',(id,data[0],relation))
            print('เชื่อมข้อมูลระหว่าง prisoner_id และ relative_id และระบุความสัมพันธ์')
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            self.close()
            self.encode_db()

    # ดึงข้อมูลผู้ต้องขังใส่ตาราง prisoners 
    @require_valid_key
    def get_data_all(self):
        self.decode_db()
        self.connect()
        try:
            if self.cursor is None:
                print("Error: Database cursor is None")
                return []
                
            self.cursor.execute('SELECT prisoner_id,sex,f_name,l_name,lawsuit,level,dan,type,status,disciplinary FROM prisoners')
            self.all_data = self.cursor.fetchall()
            return [[value if value is not None else "" for value in row] for row in self.all_data]
        except Exception as e:
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาด {e}')
            return []
        finally:
            self.close()
            self.encode_db()

    # ดึงข้อมูลผู้ต้องขัง 1 คน ในตาราง prisoners ด้วย prisoner_id
    @require_valid_key
    def get_data_one(self,prisoner_id):
        self.decode_db()
        self.connect()
        try:
            self.cursor.execute('SELECT * FROM prisoners WHERE prisoner_id = ?',(prisoner_id,))
            return self.cursor.fetchone()
        except sqlite3.OperationalError as e:
            self.msgbox(e)
            print(f'syntax ผิด / database lock : {e}')
            return False
        except sqlite3.ProgrammingError as e:
            self.msgbox(e)
            print(f'ใช้ connection หลังปิดไปแล้ว : {e}')
            return False
        except sqlite3.DatabaseError as e:
            self.msgbox(e)
            print(f'database เสียหาย : {e}')
            return False
        except Exception as e:
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาด : {e}')
            return False
        finally:
            self.close()
            self.encode_db()

    # ดึงข้อมูลญาติ โดยการค้นหาด้วย relative_id
    @require_valid_key
    def get_data_for_ralative_id(self,id):
        self.decode_db()
        self.connect()

        try:
            self.cursor.execute('SELECT * FROM relatives WHERE relative_id = ?',(id,))
            return self.cursor.fetchone()
        except sqlite3.OperationalError as e:
            self.msgbox(e)
            print(f'syntax ผิด / database lock : {e}')
            return False
        except sqlite3.ProgrammingError as e:
            self.msgbox(e)
            print(f'ใช้ connection หลังปิดไปแล้ว : {e}')
            return False
        except sqlite3.DatabaseError as e:
            self.msgbox(e)
            print(f'database เสียหาย : {e}')
            return False
        except Exception as e:
            self.msgbox(e)
            print(e)
            return False
        finally:
            self.close()
            self.encode_db()

    # ลงทะเบียนลายนิ้วมือในตาราง relatives 
    @require_valid_key
    def set_fingerprint(self,id,fingerprint):
        self.decode_db()
        self.connect()
        try:
            self.cursor.execute('UPDATE relatives SET fingerprint = ? WHERE relative_id = ?',(fingerprint,id))
            return True
        except sqlite3.OperationalError as e:
            self.msgbox(e)
            print(f'syntax ผิด / database lock : {e}')
            return False
        except sqlite3.ProgrammingError as e:
            self.msgbox(e)
            print(f'ใช้ connection หลังปิดไปแล้ว : {e}')
            return False
        except sqlite3.DatabaseError as e:
            self.msgbox(e)
            print(f'database เสียหาย : {e}')
            return False
        except Exception as e:
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาด : {e}')
            return False
        finally:
            self.close()
            self.encode_db()

    # ดึงข้อมูลญาติของผู้ต้องขัง
    @require_valid_key
    def get_join_prisoners_and_relatives_alldata(self,prisoner_id):
        self.connect()
        try:
            self.cursor.execute('''
                                    SELECT
                                        r.relative_id,
                                        r.title,
                                        r.f_name,
                                        r.l_name,
                                        r.address,
                                        r.tel,
                                        rel.relation
                                    FROM relations rel
                                    JOIN relatives r ON rel.relative_id = r.relative_id
                                    WHERE rel.prisoner_id = ?
                                ''',(prisoner_id,))
            data =  self.cursor.fetchall()
            return data
        except Exception as e:
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาด : {e}')
            return False
        finally:
            self.close()

    # ดึงข้อมูลญาติที่ไม่ใช่ผู้ติดตามของผู้ต้องขัง
    @require_valid_key
    def get_join_prisoners_and_relatives_not_follower(self,prisoner_id,national_id):
        self.connect()
        try:
            self.cursor.execute('''
                                SELECT
                                    relatives.relative_id,
                                    relatives.title,
                                    relatives.f_name,
                                    relatives.l_name
                                FROM relations
                                JOIN relatives ON relations.relative_id = relatives.relative_id
                                WHERE relations.prisoner_id = ? AND NOT relations.relative_id = ?
                                ''',(prisoner_id,national_id))
            return self.cursor.fetchall()
        except Exception as e:
            print(f'ERROR : {e}')
            self.msgbox(e)
            return False
        finally:
            self.close()

    # ดึงรหัสผู้ต้องขัง และ รหัสประจำตัวญาติ
    @require_valid_key
    def get_data_relation(self,prisoner_id):
        self.connect()
        try:
            self.cursor.execute('SELECT prisoner_id,relative_id FROM relations WHERE prisoner_id = ?',(prisoner_id,))
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            self.msgbox(e)
            print(e)
            return False
        finally:
            self.close()
    
    # ดึงข้อมูลลายนิ้วมือของญาติทุกคน
    @require_valid_key
    def get_all_fingerprint(self):
        self.connect()
        self.cursor.execute('SELECT relative_id,title,f_name,l_name,fingerprint FROM relatives')
        data = self.cursor.fetchall()
        self.close()
        return data
    
    # ดึงตารางข้อมูลผู้ต้องขัง อ้างอิงด้วย เลขบัตรประชาชนญาติ
    @require_valid_key
    def get_join_relatives_and_prisoners(self,relative_id):
        self.decode_db()
        self.connect()
        try:
            self.cursor.execute('''
                                SELECT 
                                    prisoners.prisoner_id,
                                    prisoners.f_name,
                                    prisoners.l_name,
                                    prisoners.level,
                                    prisoners.dan,
                                    relations.relation,
                                    prisoners.status,
                                    prisoners.type
                                FROM prisoners 
                                JOIN relations ON prisoners.prisoner_id = relations.prisoner_id
                                WHERE relations.relative_id = ?
                                ''',(relative_id,))
            return self.cursor.fetchall()
        except sqlite3.OperationalError as e:
            self.msgbox(e)
            print(f'syntax ผิด / database lock : {e}')
            return False
        except sqlite3.ProgrammingError as e:
            self.msgbox(e)
            print(f'ใช้ connection หลังปิดไปแล้ว : {e}')
            return False
        except sqlite3.DatabaseError as e:
            self.msgbox(e)
            print(f'database เสียหาย : {e}')
            return False
        except Exception as e:
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาด : {e}')
            return False
        finally:
            self.close()
            self.encode_db()

    # เพิ่มข้อมูลการเยี่ยมลงตาราง visit
    @require_valid_key
    def add_visits(self,query,data):
        # print(f'{query},',data)
        self.decode_db()
        self.connect()
        try:
            self.cursor.execute(query,data)
            return True
        except Exception as e:
            self.msgbox(e)
            print(f'Error : {e}')
            return False
        finally:
            self.close()
            self.encode_db()

    # เพิ่มช่องเยี่ยม
    @require_valid_key
    def add_channel_on_visits(self,data,channel):
        self.connect()
        try:
            self.cursor.execute('''
                                UPDATE visits
                                SET channel = ?
                                WHERE date_visit = ? AND time_visit = ? AND prisoner_id = ? AND relative_id_1 = ?
                                ''', (channel, data[0], data[1], data[2], data[3]))
            return True
        except Exception as e:
            self.msgbox(e)
            return False
        finally:
            self.close()


    # รายงานการเยี่ยมประจำวัน
    @require_valid_key
    def get_visits_on_db(self,data_visit):
        # self.decode_db()
        self.connect()
        try:
            self.cursor.execute('''
                                SELECT
                                    visits.visit_id,
                                    visits.time_stamp,
                                    visits.date_visit,
                                    visits.time_visit,
                                    prisoners.f_name || " " || prisoners.l_name AS prisoner_name,
                                    COALESCE(r1.title || " " || r1.f_name || " " || r1.l_name, '-') AS relative_1,
                                    COALESCE(r2.title || " " || r2.f_name || " " || r2.l_name, '-') AS relative_2,
                                    COALESCE(r3.title || " " || r3.f_name || " " || r3.l_name, '-') AS relative_3,
                                    COALESCE(r4.title || " " || r4.f_name || " " || r4.l_name, '-') AS relative_4,
                                    COALESCE(r5.title || " " || r5.f_name || " " || r5.l_name, '-') AS relative_5,
                                    visits.channel
                                FROM
                                    visits
                                JOIN prisoners ON visits.prisoner_id = prisoners.prisoner_id
                                LEFT JOIN relatives AS r1 ON visits.relative_id_1 = r1.relative_id
                                LEFT JOIN relatives AS r2 ON visits.relative_id_2 = r2.relative_id
                                LEFT JOIN relatives AS r3 ON visits.relative_id_3 = r3.relative_id
                                LEFT JOIN relatives AS r4 ON visits.relative_id_4 = r4.relative_id
                                LEFT JOIN relatives AS r5 ON visits.relative_id_5 = r5.relative_id
                                WHERE 
                                    visits.date_visit = ? AND visits.time_visit = ? ''',
                                    (data_visit[0],data_visit[1])
                                )
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            self.msgbox(e)
            return False
        finally:
            self.close()
            # self.encode_db()

    # ดึง ไอดี ชื่อ สกุล ของตารางญาติ
    @require_valid_key
    def get_relatives_id_fname_lname(self):
        self.decode_db()
        self.connect()

        try:
            self.cursor.execute('SELECT relative_id,f_name,l_name FROM relatives')
            return self.cursor.fetchall()
        except Exception as e:
            self.msgbox(e)
            return False
        finally:
            self.close()
            self.encode_db()
            
    # ดึงข้อมูลการเยี่ยมประจำเดือน
    @require_valid_key
    def get_visits_by_month(self, data_month):
        """ดึงข้อมูลการเยี่ยมทั้งเดือน"""
        self.decode_db()
        self.connect()
        try:
            self.cursor.execute('''
                                SELECT
                                    visits.visit_id,
                                    visits.time_stamp,
                                    visits.date_visit,
                                    visits.time_visit,
                                    prisoners.f_name || " " || prisoners.l_name AS prisoner_name,
                                    COALESCE(r1.title || " " || r1.f_name || " " || r1.l_name, '-') AS relative_1,
                                    COALESCE(r2.title || " " || r2.f_name || " " || r2.l_name, '-') AS relative_2,
                                    COALESCE(r3.title || " " || r3.f_name || " " || r3.l_name, '-') AS relative_3,
                                    COALESCE(r4.title || " " || r4.f_name || " " || r4.l_name, '-') AS relative_4,
                                    COALESCE(r5.title || " " || r5.f_name || " " || r5.l_name, '-') AS relative_5,
                                    visits.channel
                                FROM
                                    visits
                                JOIN prisoners ON visits.prisoner_id = prisoners.prisoner_id
                                LEFT JOIN relatives AS r1 ON visits.relative_id_1 = r1.relative_id
                                LEFT JOIN relatives AS r2 ON visits.relative_id_2 = r2.relative_id
                                LEFT JOIN relatives AS r3 ON visits.relative_id_3 = r3.relative_id
                                LEFT JOIN relatives AS r4 ON visits.relative_id_4 = r4.relative_id
                                LEFT JOIN relatives AS r5 ON visits.relative_id_5 = r5.relative_id
                                WHERE 
                                    strftime('%Y', visits.date_visit) = ? AND strftime('%m', visits.date_visit) = ?
                                ORDER BY visits.date_visit, visits.time_visit''',
                                    (data_month[0], data_month[1])
                                )
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            self.msgbox(e)
            return False
        finally:
            self.close()
            self.encode_db()

    # ดึงข้อมูลของญาติด้วย เลขบัตรประชาชน   
    @require_valid_key
    def get_relative_by_national_id(self,id):
        self.connect()
        try:
            self.cursor.execute('SELECT title,f_name,l_name FROM relatives WHERE relative_id = ?',(id,))
            return self.cursor.fetchall()
        except Exception as e:
            self.msgbox(e)
            return False
        finally:
            self.close()

    # นับครั้งการเยี่ยม เงื่อนไขตามชั้น
    @require_valid_key
    def get_count_visit(self,prisoner_id,today,month):
        self.decode_db()
        self.connect()

        try:
            self.cursor.execute('SELECT COUNT(*) FROM visits WHERE prisoner_id = ? AND date_visit = ?',(prisoner_id,today))
            count_today = self.cursor.fetchone()[0]
            self.cursor.execute('SELECT COUNT(*) FROM visits WHERE prisoner_id = ? AND strftime("%Y-%m", date_visit) = ?',(prisoner_id,month))
            count_month = self.cursor.fetchone()[0]
            return count_today,count_month
        except Exception as e:
            self.msgbox(e)
            return False
        finally:
            self.close()
            self.encode_db()

    # นับครั้งการเยี่ยม ประจำวัน
    @require_valid_key
    def get_count_visit_on_round(self,round_time,date_current):
        self.decode_db()
        self.connect()
        print(round_time,date_current)

        try:
            self.cursor.execute('SELECT count (*) FROM visits WHERE time_visit = ? AND date_visit = ?',(round_time,date_current))
            count = self.cursor.fetchone()[0]
            return count
        except Exception as e:
            self.msgbox(e)  
            return False
        finally:
            self.close()
            self.encode_db()

    # แก้ไขชั้นและแดน
    @require_valid_key
    def update_level_and_dan(self,id,sex,f_name,l_name,lawsuit,level,dan,type_data,status,disciplinary):
        self.connect()
        try:
            disciplinary_values = None if disciplinary == 'ไม่มี' else disciplinary
            print(id,level,dan,type_data,status,disciplinary)
            self.cursor.execute('''UPDATE 
                                    prisoners 
                                SET 
                                    sex = ? ,
                                    f_name = ? ,
                                    l_name = ? ,
                                    lawsuit = ? ,
                                    level = ? ,
                                    dan = ?,
                                    type = ?,
                                    status = ?,
                                    disciplinary = ?
                                WHERE 
                                    prisoner_id = ?''',(sex,f_name,l_name,lawsuit,level,dan,type_data,status,disciplinary_values,id))
            return True
        except Exception as e:
            self.msgbox(e)
            return False
        finally:
            self.close()    

    # ดึงข้อมูลญาติทั้งหมดใน DB
    @require_valid_key
    def get_all_relatives(self):
        self.connect()
        try:
            if self.cursor is None:
                print("Error: Database cursor is None")
                return []
                
            self.cursor.execute('SELECT relative_id,title,f_name,l_name,address,tel FROM relatives')
            result = self.cursor.fetchall()
            return result if result else []
        except Exception as e:
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาดใน get_all_relatives: {e}')
            return []
        finally:
            self.close()

    # ลบข้อมูลญาติ
    @require_valid_key
    def delete_relation_from_prisoner_and_relative(self,prisoner_id,relative_id):
        print(prisoner_id,relative_id)
        self.connect()
        try:
            self.cursor.execute('DELETE FROM relations WHERE prisoner_id = ? AND relative_id = ?',(prisoner_id,relative_id))
            return True
        except Exception as e:
            self.msgbox(e)
            return False
        finally:
            self.close()

    # ลบข้อมูลผู้ต้องขัง
    @require_valid_key
    def delete_prisoner(self,id):
        self.connect()
        try:
            print(type(id))
            self.cursor.execute('DELETE FROM prisoners WHERE prisoner_id = ?',(id,))
            return True
        except Exception as e:
            self.msgbox(e)
            return False
        finally:
            self.close()

    # แก้ไขข้อมูลญาติ
    @require_valid_key
    def edit_relative(self,data,id):
        self.connect()
        try:
            self.cursor.execute('UPDATE relatives SET title = ?, f_name = ?, l_name = ?, address = ?, tel = ? WHERE relative_id = ?',(*data, id))
            return True
        except Exception as e:
            self.msgbox(e)
            print(e)
            return False
        finally:
            self.close()
            
    # ย้ายรอบเยี่ยม
    @require_valid_key
    def update_visit_round(self,new_round,visit_id):
        self.decode_db()
        self.connect()
        try:
            self.cursor.execute('UPDATE visits SET time_visit = ? WHERE visit_id = ?',(new_round,visit_id))
            return True
        except Exception as e:
            self.msgbox(e)
            return False
        finally:
            self.close()

    # ลบข้อมูลการเยี่ยม
    @require_valid_key
    def remove_visit(self,visit_id):
        self.decode_db()
        self.connect()
        try:
            self.cursor.execute('DELETE FROM visits WHERE visit_id = ?',(visit_id,))
            return True
        except Exception as e:
            self.msgbox(e)
            return False
        finally:
            self.close()

    # ดึงข้อมูลตาราง visits ทั้งหมดอ้างอิงด้วย visit_id
    @require_valid_key
    def get_visit_by_id(self,visit_id):
        self.decode_db()
        self.connect()
        try:
            self.cursor.execute('SELECT * FROM visits WHERE visit_id = ?',(visit_id,))
            return self.cursor.fetchone()
        except Exception as e:
            self.msgbox(e)
            return False
        finally:
            self.close()

    # ดึงข้อมูลญาติ เลขบัตร คำนำหน้า ชื่อ สกุล
    @require_valid_key
    def get_join_prisoners_and_relatives(self,prisoner_id):
        self.connect()
        try:
            self.cursor.execute('''
                                SELECT
                                    relatives.relative_id,
                                    relatives.title,
                                    relatives.f_name,
                                    relatives.l_name
                                FROM relations
                                JOIN relatives ON relations.relative_id = relatives.relative_id
                                WHERE relations.prisoner_id = ?
                                ''',(prisoner_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f'ERROR : {e}')
            self.msgbox(e)
            return False
        finally:
            self.close()

    # เช็คข้อมูลความสัมพันธ์ ถ้า 1 คือ มี 0 คือ ไม่มี
    @require_valid_key
    def count_relative(self,prisoner_id,relative_id):
        self.connect()
        try:
            self.cursor.execute('SELECT count (*) FROM relations WHERE prisoner_id = ? AND relative_id = ?',(prisoner_id,relative_id,))
            count = self.cursor.fetchone()[0]
            return count
        except Exception as e:
            print(e)
            self.msgbox(e)
            return False
        finally:
            self.close()

    # ดึงข้อมูลตารางเยี่ยม โดยใช้ visit_id
    @require_valid_key
    def prisoner_id_on_table_visits(self,visit_id):
        print(f'visit_id on db = {visit_id}')
        self.connect()
        try:
            self.cursor.execute('SELECT prisoner_id FROM visits WHERE visit_id = ?',(visit_id,))
            data = self.cursor.fetchone()[0]
            return data
        except Exception as e:
            print(e)
            self.msgbox(e)
            return False
        finally:
            self.close()

    # execute ดึงข้อมูล โดยการส่ง query เอง
    @require_valid_key
    def get_execute_manual(self,query):
        self.connect()
        try:
            self.cursor.execute(query)
            data = self.cursor.fetchone()[0]
            # print(data)
            return data
        except Exception as e:
            print(e)
            self.msgbox(e)
            return False
        finally:
            self.close()

    # execute ส่งข้อมูล โดยการส่ง query เอง
    @require_valid_key
    def set_execute_manual(self,query,params = None):
        self.connect()
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return True
        except Exception as e:
            print(e)
            self.msgbox(e)
            return False
        finally:
            self.close()

    # เพิ่มข้อมูลในตาราง visits เพิ่มเติม
    @require_valid_key
    def add_relative_to_visits(self,data):
        self.connect()
        try:
            self.cursor.execute('UPDATE visits SET relative_id_1 = ?,relative_id_2 = ?,relative_id_3 = ?,relative_id_4 = ?,relative_id_5 =? WHERE visit_id = ?',(data))
            return True
        except Exception as e:
            print(e)
            self.msgbox(e)
            return False
        finally:
            self.close()

    # ฟังก์ชันแก้ไขความสัมพันธ์ของญาติและผู้ต้องขัง
    @require_valid_key
    def edit_relation(self,relation,relative_id,prisoner_id):
        self.connect()
        try:
            self.cursor.execute('UPDATE relations SET relation = ? WHERE prisoner_id = ? AND relative_id = ?',(relation,prisoner_id,relative_id))
            return True
        except Exception as e:
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาด : {e}')
            return False
        finally:
            self.close()
            
    # รดึงค่าความสัมพันธ์ของญาติและผู้ต้องขัง
    @require_valid_key
    def get_relation(self,prisoner_id,relative_id):
        self.connect()
        try:
            self.cursor.execute('SELECT relation FROM relations WHERE prisoner_id = ? AND relative_id = ?',(prisoner_id,relative_id))
            return self.cursor.fetchone()[0]
        except Exception as e:
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาด : {e}')
            return False
        finally:
            self.close()

    # ดึงข้อมูลเยี่ยมจากตารางเยี่ยม visits โดยดึงจากวันที่
    @require_valid_key
    def get_visits_all_on_date(self,date):
        self.connect()
        try:   
            self.cursor.execute('SELECT * FROM visits WHERE date_visit = ?',(date,))
            return self.cursor.fetchall()
        except Exception as e:
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาด : {e}')
            return False
        finally:
            self.close()

    def get_users(self):
        self.connect()
        users = {}
        try:
            self.cursor.execute('SELECT username,password,user_type,fullname FROM users')
            for username,password,user_type,fullname in self.cursor.fetchall():
                users[username] = {
                    'password': password,
                    'user_type': user_type,
                    'fullname': fullname
                }
        except Exception as e:
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาด : {e}')
            return False
        finally:
            self.close()
        return users



    def decode_db(self):
        return
        if self.EN_DB and os.path.exists(self.EN_DB):
            try:
                decrypt_file(self.EN_DB, self.DE_DB)
            except Exception as e:
                self.msgbox(f'ถอดรหัสฐานข้อมูลล้มเหลว: {e}')

    def encode_db(self):
        return
        try:
            encrypt_file(self.DE_DB, self.EN_DB)
        except Exception as e:
            self.msgbox(f'เข้ารหัสฐานข้อมูลล้มเหลว: {e}')


########################################################## 
# สำหรับการเข้าใู
# ########################################################
