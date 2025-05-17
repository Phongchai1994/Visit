import sqlite3
import os
from manage.encryption_utils import decrypt_file,encrypt_file
import customtkinter as ctk
from tkinter import messagebox
import json
from pathlib import Path
import tempfile
import sys

TEMP_DIR = Path(tempfile.gettempdir()) # สร้างไฟล์ชั่วคราวไว้ใน Temp

def get_config_path():
    return os.path.join(os.getcwd(), "config", "config.json")

def load_config():
    config_path = get_config_path()
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f).get('db_path')
    return ''

class SQLiteDB:
    def __init__(self,db_path=load_config()):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        # โปรแกรมถอดรหัส และเข้ารหัส
        # self.EN_DB = load_config()  # โหลดข้อมูลจาก ไฟล์ config.json
        # self.DE_DB = TEMP_DIR / 'visit_report.db'

    def msgbox(self,e):
        messagebox.showerror('ฐานข้อมูล',f'{e}')

    def connect(self):
        try:
            self.conn =sqlite3.connect(self.db_path)
            self.conn.execute('PRAGMA foreign_keys = ON')
            self.cursor = self.conn.cursor()
        except Exception as e:
            messagebox.showerror('เชื่อมต่อฐานข้อมูลไม่สำเร็จ',e)

        print('เชื่อมต่อฐานข้อมูล')

    def close(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()
            self.conn = None
            self.cursor = None
            print('ปิดฐานข้อมูล')

    def add_data(self,data):
        self.decode_db()
        self.connect()
        try :
            print('กำลังบันทึกข้อมูล')
            self.cursor.execute('INSERT INTO prisoners (prisoner_id,sex,f_name,l_name,lawsuit,level,dan) VALUES (?,?,?,?,?,?,?)',data)
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
    
    def add_data_ralative_to_relatives(self,id,data,relation):
        self.decode_db()
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

    def get_data_all(self):
        self.decode_db()
        self.connect()
        try:
            self.cursor.execute('SELECT prisoner_id,sex,f_name,l_name,lawsuit,level,dan FROM prisoners')
            self.all_data = self.cursor.fetchall()
            return self.all_data
        except Exception as e:
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาด {e}')
            return False
        finally:
            self.close()
            self.encode_db()

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

    def get_join_prisoners_and_relatives(self,prisoner_id):
        self.decode_db()
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
    
    def get_join_prisoners_and_relatives_not_follower(self,prisoner_id,national_id):
        self.decode_db()
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
            self.encode_db()

    def get_data_relation(self,id):
        self.decode_db()
        self.connect()

        try:
            self.cursor.execute('SELECT prisoner_id,relative_id FROM relations WHERE prisoner_id = ?',(id,))
            result = self.cursor.fetchall()
            print(result)
            return result
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
    
    def get_all_fingerprint(self):
        self.decode_db()
        self.connect()

        self.cursor.execute('SELECT relative_id,title,f_name,l_name,fingerprint FROM relatives')
        data = self.cursor.fetchall()
        self.close()
        self.encode_db()

        return data

    def get_join_relatives_and_prisoners(self,id):
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
                                    relations.relation
                                FROM prisoners 
                                JOIN relations ON prisoners.prisoner_id = relations.prisoner_id
                                WHERE relations.relative_id = ?
                                ''',(id,))
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

    def add_data_visits_to_db(self,data):
        self.decode_db()
        self.connect()
        try:
            self.cursor.execute('''
                                INSERT INTO visits 
                                (date_reserve,
                                time_reserve,
                                prisoner_id,
                                relative_id_1,
                                relative_id_2,
                                relative_id_3,
                                relative_id_4,
                                relative_id_5) 
                                VALUES (?,?,?,?,?,?,?,?)
                                ''',(data))
        except Exception as e:
            self.msgbox(e)
            print(f'Error : {e}')
        finally:
            self.close()
            self.encode_db()

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

    def get_visits(self,data_visit):
        self.decode_db()
        self.connect()
        try:
            self.cursor.execute('''
                                SELECT
                                    visits.time_stamp,
                                    visits.date_visit,
                                    visits.time_visit,
                                    prisoners.f_name || " " || prisoners.l_name AS prisoner_name,
                                    COALESCE(r1.title || " " || r1.f_name || " " || r1.l_name, '-') AS relative_1,
                                    COALESCE(r2.title || " " || r2.f_name || " " || r2.l_name, '-') AS relative_2,
                                    COALESCE(r3.title || " " || r3.f_name || " " || r3.l_name, '-') AS relative_3,
                                    COALESCE(r4.title || " " || r4.f_name || " " || r4.l_name, '-') AS relative_4,
                                    COALESCE(r5.title || " " || r5.f_name || " " || r5.l_name, '-') AS relative_5
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
            self.encode_db()

    # ดึง ไอดี ชื่อ สกุล ของตารางญาติ
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

    # นับครั้งการเยี่ยม เงื่อนไขตามชั้น
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
    def update_level_and_dan(self,id,level,dan):
        self.connect()
        try:
            self.cursor.execute('UPDATE prisoners SET level = ? ,dan = ? WHERE prisoner_id = ?',(level,dan,id))
            return True
        except Exception as e:
            self.msgbox(e)
            return False
        finally:
            self.close()    

    # ดึงข้อมูลญาติทั้งหมดใน DB
    def get_all_relatives(self):
        self.connect()
        try:
            self.cursor.execute('SELECT relative_id,title,f_name,l_name,address,tel FROM relatives')
            return self.cursor.fetchall()
        except Exception as e:
            self.msgbox(e)
            return False
        finally:
            self.close()

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

