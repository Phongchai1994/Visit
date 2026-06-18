import os
import sys
from manage.encryption_utils import decrypt_file,encrypt_file
from tkinter import messagebox
import json
from pathlib import Path
import tempfile
import datetime
import psycopg2
from psycopg2 import Binary
from dotenv import load_dotenv
from manage import config

TODAYS = datetime.datetime.today()
TODAYS_STR = TODAYS.strftime("%Y-%m-%d")


TEMP_DIR = Path(tempfile.gettempdir()) # สร้างไฟล์ชั่วคราวไว้ใน Temp

def check_key_on_db():
    connection_params = {
        'host': os.getenv("PG_HOST"),
        'port': os.getenv("PG_PORT"),
        'dbname': os.getenv("PG_NAME"),
        'user': os.getenv("PG_USER"),
        'password': os.getenv("PG_PASS")
    }
    with psycopg2.connect(**connection_params) as conn:
        conn.autocommit(True)
        with conn.cursor() as cur:
            cur.execute('SELECT key FROM check_')
            result = cur.fetchone()
            conn.close()
            return result[0] if result else None

def require_valid_key(func):
    KEY = 'E54F2JN5F3'
    def wrapper(self, *args, **kwargs):
        KEY_DB = check_key_on_db()  # <-- เรียกทุกครั้งที่ใช้งาน
        if KEY_DB != KEY:
            messagebox.showerror("แจ้งอัพเดท","กรุณาอัพเดทโปรแกรม")
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
        self.create_table()
        # โปรแกรมถอดรหัส และเข้ารหัส
        # self.EN_DB = load_config()  # โหลดข้อมูลจาก ไฟล์ config.json
        # self.DE_DB = TEMP_DIR / 'visit_report.db'
    def create_table(self):
        # ตารางจองเยี่ยมวันหยุดพิเศษ
        def visit_spacial_table():
            self.connect()
            try:
                self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS "visit_spacial" (
                        "visit_id" INTEGER NOT NULL,
                        "time_stamp" TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                        "date_visit" TEXT NOT NULL,
                        "time_visit" TEXT NOT NULL,
                        "prisoner_id" INTEGER NOT NULL,
                        "relative_id_1" INTEGER,
                        "relative_id_2" INTEGER,
                        "relative_id_3" INTEGER,
                        "relative_id_4" INTEGER,
                        "relative_id_5" INTEGER,
                        "channel" INTEGER,
                        PRIMARY KEY("visit_id" AUTOINCREMENT)
                    )
                ''')
                # print('สร้างตาราง visit_spacial สำเร็จ')
                return True
            except Exception as e:
                import sys
                func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
                self.log_error([func_name,str(e)])
                print(f'ข้อผิดพลาด: {e}')
                return False
            finally:
                self.close()

        def log_error():
            self.connect()
            try:
                self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS "log_error" (
                        log_id INTEGER NOT NULL,
                        time_stamp TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                        function_name TEXT,
                        error_message TEXT,
                        extra_info TEXT,
                        PRIMARY KEY("log_id" AUTOINCREMENT)
                    )
                ''')
                # print('สร้างตาราง log_error สำเร็จ')
                return True
            except Exception as e:
                import sys
                func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
                self.log_error([func_name,str(e)])
                print(f'ข้อผิดพลาด: {e}')
                return False
            finally:
                self.close()
        
        def create_all_tables():
            """สร้างตารางทั้งหมดตาม Structure ที่กำหนด"""
            self.connect()
            try:
                # 1. ตาราง prisoners_
                self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS "prisoners_" (
                        "prisoner_id" INTEGER NOT NULL,
                        "sex" TEXT NOT NULL,
                        "f_name" TEXT NOT NULL,
                        "l_name" TEXT NOT NULL,
                        "lawsuit" TEXT NOT NULL,
                        "level" TEXT NOT NULL,
                        "dan" TEXT NOT NULL,
                        "type" TEXT,
                        "status" TEXT,
                        "disciplinary" TEXT,
                        PRIMARY KEY("prisoner_id")
                    )
                ''')

                # 2. ตาราง relatives
                self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS "relatives" (
                        "relative_id" INTEGER NOT NULL UNIQUE,
                        "title" TEXT NOT NULL,
                        "f_name" TEXT NOT NULL,
                        "l_name" TEXT NOT NULL,
                        "address" TEXT NOT NULL,
                        "tel" TEXT NOT NULL,
                        "fingerprint" BLOB,
                        PRIMARY KEY("relative_id")
                    )
                ''')

                # 3. ตาราง relations
                self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS "relations" (
                        "id" INTEGER NOT NULL UNIQUE,
                        "prisoner_id" INTEGER NOT NULL,
                        "relative_id" INTEGER NOT NULL,
                        "relation" TEXT NOT NULL,
                        PRIMARY KEY("id" AUTOINCREMENT)
                    )
                ''')

                # 4. ตาราง visits
                self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS "visits" (
                        "visit_id" INTEGER NOT NULL,
                        "time_stamp" TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                        "date_visit" TEXT NOT NULL,
                        "time_visit" TEXT NOT NULL,
                        "prisoner_id" INTEGER NOT NULL,
                        "relative_id_1" INTEGER,
                        "relative_id_2" INTEGER,
                        "relative_id_3" INTEGER,
                        "relative_id_4" INTEGER,
                        "relative_id_5" INTEGER,
                        "channel" INTEGER,
                        PRIMARY KEY("visit_id" AUTOINCREMENT)
                    )
                ''')

                # 5. ตาราง visit_spacial (จากตัวอย่างแรกที่คุณให้มา)
                self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS "visit_spacial" (
                        "visit_id" INTEGER NOT NULL,
                        "time_stamp" TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                        "date_visit" TEXT NOT NULL,
                        "time_visit" TEXT NOT NULL,
                        "prisoner_id" INTEGER NOT NULL,
                        "relative_id_1" INTEGER,
                        "relative_id_2" INTEGER,
                        "relative_id_3" INTEGER,
                        "relative_id_4" INTEGER,
                        "relative_id_5" INTEGER,
                        "channel" INTEGER,
                        PRIMARY KEY("visit_id" AUTOINCREMENT)
                    )
                ''')

                # print("สร้างตารางทั้งหมดในระบบเรียบร้อยแล้ว")
                return True
            except Exception as e:
                func_name = sys._getframe().f_code.co_name
                self.log_error([func_name, str(e)])
                print(f"เกิดข้อผิดพลาดในการสร้างตาราง: {e}")
                return False
            finally:
                self.close()
        # เรียกใช้การสร้างตาราง
        visit_spacial_table()
        log_error()
        create_all_tables()

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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาด : {e}')
            return False
        finally:
            self.close()
    # ถึงข้อมูลช่องด้วย วันที่ และเวลา ของตารางเยี่ยมพิเศษ

    def get_dashboard_summary(self,date_str):
        """ดึงข้อมูลสรุป Dashboard"""
        self.connect()
        try:
            # ผู้ต้องขังทั้งหมด (สถานะปกติ)
            self.cursor.execute("SELECT COUNT(*) FROM prisoners_ WHERE status = 'อยู่' AND type = 'ผู้ต้องขัง'")
            prisoner_normal = self.cursor.fetchone()[0]

            # จำนวนผู้ต้องขังชาย
            self.cursor.execute("SELECT COUNT(*) FROM prisoners_ WHERE status = 'อยู่' AND sex = 'ชาย' AND type = 'ผู้ต้องขัง'")
            prisoner_male = self.cursor.fetchone()[0]

            # จำนวนผู้ต้องขังหญิง
            self.cursor.execute("SELECT COUNT(*) FROM prisoners_ WHERE status = 'อยู่' AND sex = 'หญิง' AND type = 'ผู้ต้องขัง'")
            prisoner_female = self.cursor.fetchone()[0]

            # ผู้ต้องกักขังทั้งหมด
            self.cursor.execute("SELECT COUNT(*) FROM prisoners_ WHERE type = 'ผู้ต้องกักขัง' AND status = 'อยู่'")
            prisoner_detained = self.cursor.fetchone()[0]

            # จำนวนผู้ต้องกักขังชาย
            self.cursor.execute("SELECT COUNT(*) FROM prisoners_ WHERE type = 'ผู้ต้องกักขัง' AND status = 'อยู่' AND sex = 'ชาย'")
            detained_male = self.cursor.fetchone()[0]

            # จำนวนผู้ต้องกักขังหญิง
            self.cursor.execute("SELECT COUNT(*) FROM prisoners_ WHERE type = 'ผู้ต้องกักขัง' AND status = 'อยู่' AND sex = 'หญิง'")
            detained_female = self.cursor.fetchone()[0]

            # ผิดวินัยกี่คน
            self.cursor.execute("SELECT COUNT(*) FROM prisoners_ WHERE disciplinary = 'ผิดวินัย' AND status = 'อยู่'")
            prisoner_disciplinary = self.cursor.fetchone()[0]

            # ผิดวินัยชาย
            self.cursor.execute("SELECT COUNT(*) FROM prisoners_ WHERE disciplinary = 'ผิดวินัย' AND status = 'อยู่' AND sex = 'ชาย'")
            prisoner_disciplinary_male = self.cursor.fetchone()[0]            
            
            # ผิดวินัยหญิง
            self.cursor.execute("SELECT COUNT(*) FROM prisoners_ WHERE disciplinary = 'ผิดวินัย' AND status = 'อยู่' AND sex = 'หญิง'")
            prisoner_disciplinary_female = self.cursor.fetchone()[0]

            # ญาติทั้งหมด
            self.cursor.execute("SELECT COUNT(*) FROM relatives")
            relatives_total = self.cursor.fetchone()[0]

            # ญาติชาย
            self.cursor.execute("SELECT COUNT(*) FROM relatives WHERE title IN ('นาย','ด.ช.','เด็กชาย','พระ')")
            relatives_male = self.cursor.fetchone()[0]            
            
            # ญาติหญิง
            self.cursor.execute("SELECT COUNT(*) FROM relatives WHERE title IN ('นาง','น.ส.','นางสาว','ด.ญ.','เด็กหญิง')")
            relatives_female = self.cursor.fetchone()[0]

            # วันนี้มีผู้ต้องขังได้เยี่ยมกี่คน (ไม่ซ้ำ)
            self.cursor.execute("SELECT COUNT(DISTINCT prisoner_id) FROM visits WHERE date_visit = ?",(date_str,))
            prisoner_visited_today = self.cursor.fetchone()[0]

            # วันนี้ญาติเข้าเยี่ยมกี่คน (รวมทุกช่อง)
            self.cursor.execute("""
                SELECT COUNT(*) FROM (
                    SELECT relative_id_1 AS rid FROM visits WHERE date_visit = ? AND relative_id_1 IS NOT NULL AND relative_id_1 != ''
                    UNION ALL SELECT relative_id_2 FROM visits WHERE date_visit = ? AND relative_id_2 IS NOT NULL AND relative_id_2 != ''
                    UNION ALL SELECT relative_id_3 FROM visits WHERE date_visit = ? AND relative_id_3 IS NOT NULL AND relative_id_3 != ''
                    UNION ALL SELECT relative_id_4 FROM visits WHERE date_visit = ? AND relative_id_4 IS NOT NULL AND relative_id_4 != ''
                    UNION ALL SELECT relative_id_5 FROM visits WHERE date_visit = ? AND relative_id_5 IS NOT NULL AND relative_id_5 != ''
                ) WHERE rid IS NOT NULL AND rid != ''
            """, (date_str, date_str, date_str, date_str, date_str))
            relatives_visited_today = self.cursor.fetchone()[0]

            # ญาติชาย (รวมซ้ำทุกช่อง)
            self.cursor.execute("""
                SELECT COUNT(*) FROM (
                    SELECT r.title
                    FROM (
                        SELECT relative_id_1 AS rid FROM visits WHERE date_visit = ? AND relative_id_1 IS NOT NULL
                        UNION ALL SELECT relative_id_2 FROM visits WHERE date_visit = ? AND relative_id_2 IS NOT NULL
                        UNION ALL SELECT relative_id_3 FROM visits WHERE date_visit = ? AND relative_id_3 IS NOT NULL
                        UNION ALL SELECT relative_id_4 FROM visits WHERE date_visit = ? AND relative_id_4 IS NOT NULL
                        UNION ALL SELECT relative_id_5 FROM visits WHERE date_visit = ? AND relative_id_5 IS NOT NULL
                    ) v
                    JOIN relatives r ON v.rid = r.relative_id
                    WHERE r.title IN ('นาย','ด.ช.','เด็กชาย','พระ')
                )
            """, (date_str, date_str, date_str, date_str, date_str))
            relatives_visited_male_today = self.cursor.fetchone()[0]

            # ญาติหญิง (รวมซ้ำทุกช่อง)
            self.cursor.execute("""
                SELECT COUNT(*) FROM (
                    SELECT r.title
                    FROM (
                        SELECT relative_id_1 AS rid FROM visits WHERE date_visit = ? AND relative_id_1 IS NOT NULL
                        UNION ALL SELECT relative_id_2 FROM visits WHERE date_visit = ? AND relative_id_2 IS NOT NULL
                        UNION ALL SELECT relative_id_3 FROM visits WHERE date_visit = ? AND relative_id_3 IS NOT NULL
                        UNION ALL SELECT relative_id_4 FROM visits WHERE date_visit = ? AND relative_id_4 IS NOT NULL
                        UNION ALL SELECT relative_id_5 FROM visits WHERE date_visit = ? AND relative_id_5 IS NOT NULL
                    ) v
                    JOIN relatives r ON v.rid = r.relative_id
                    WHERE r.title IN ('นาง','น.ส.','นางสาว','ด.ญ.','เด็กหญิง')
                )
            """, (date_str, date_str, date_str, date_str, date_str))
            relatives_visited_female_today = self.cursor.fetchone()[0]

            return {
                "prisoner_normal": prisoner_normal,
                "prisoner_male": prisoner_male,
                "prisoner_female": prisoner_female,
                "prisoner_detained": prisoner_detained,
                "detained_male": detained_male,
                "detained_female": detained_female,
                "prisoner_disciplinary": prisoner_disciplinary,
                "prisoner_disciplinary_male": prisoner_disciplinary_male,
                "prisoner_disciplinary_female": prisoner_disciplinary_female,
                "relatives_total": relatives_total,
                "relatives_male": relatives_male,
                "relatives_female": relatives_female,
                "prisoner_visited_today": prisoner_visited_today,
                "relatives_visited_today": relatives_visited_today,
                "relatives_visited_male_today": relatives_visited_male_today,
                "relatives_visited_female_today": relatives_visited_female_today,

            }
        except Exception as e:
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name, str(e)])
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาด : {e}')
            return None
        finally:
            self.close()

    def log_error(self,log_data):
        '''
        บันทึก log error ใน database
        '''
        self.connect()
        try:
            # เติม None ให้ครบ 3 ค่า
            data = list(log_data) + [None] * (3 - len(log_data))
            self.cursor.execute(
                'INSERT INTO log_error (function_name, error_message, extra_info) VALUES (?, ?, ?)',
                data[:3]
            )
            self.conn.commit()
            return True
        except Exception as e:
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาด : {e}')
            return False
        finally:
            self.close()

    def get_log(self):
        self.connect()
        try:
            self.cursor.execute('SELECT * FROM log_error ORDER BY time_stamp DESC')
            return self.cursor.fetchall()    
        except Exception as e:
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาด : {e}')
            return False
        finally:
            self.close()

    @require_valid_key
    def get_chanel_on_visit_spacial(self,time_,date_):
        self.connect()
        try:

            self.cursor.execute('SELECT count (*) FROM visit_spacial WHERE time_visit = ? AND date_visit = ?',(time_,date_))
            count = self.cursor.fetchone()[0]
            return count      
        except Exception as e:
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาด : {e}')
            return False
        finally:
            self.close()

    # ตารางเยี่ยมพิเศษ ตรวจสอบว่าผู้ต้องขังได้เยี่ยมหรือยัง ต่อวัน
    @require_valid_key
    def check_visit_spacial_log(self,prisoner_id,date):
        self.connect()
        try:
            self.cursor.execute('SELECT count (*) FROM visit_spacial WHERE prisoner_id = ? AND date_visit = ?',(prisoner_id,date))
            count = self.cursor.fetchone()[0]
            return count      
        except Exception as e:
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาด : {e}')
            return False
        finally:
            self.close()

    # ตารางเยี่ยมพิเศษ เพิ่มข้อมูลการเยี่ยมลงในตาราง
    @require_valid_key
    def add_visit_to_visit_spacial(self,query,data):
        self.connect()
        try:
            self.cursor.execute(query,data)
            return True
        except Exception as e:
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาด : {e}')
            return False
        finally:
            self.close()

    # ตารางเยี่ยมพิเศษ ดึงข้อมูล ช่องเยี่ยม
    @require_valid_key
    def get_chanel_blank_on_visit_spacial(self,time,date):
        # print(f'time = {time} date = {date}')
        self.connect()
        try:
            self.cursor.execute('SELECT channel FROM visit_spacial WHERE date_visit = ? AND time_visit = ?',(date,time))
            data = [row[0] for row in self.cursor.fetchall() if row[0] is not None]
            # print(f'data = {data}')
            return data
        
        except Exception as e:
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาด : {e}')
            return False
        finally:
            self.close()

    # ตารางเยี่ยมพิเศษ ดึงข้อมูล ปี เดือน วัน และส่งกลับค่าเดียว
    @require_valid_key
    def get_date_on_visit_spacial(self):
        self.connect()
        try:
            self.cursor.execute("SELECT DISTINCT strftime('%Y', date_visit) FROM visit_spacial ORDER BY 1")
            years = [row[0] for row in self.cursor.fetchall()]
            self.cursor.execute("SELECT DISTINCT strftime('%m', date_visit) FROM visit_spacial ORDER BY 1")
            months = [row[0] for row in self.cursor.fetchall()]
            self.cursor.execute("SELECT DISTINCT strftime('%d', date_visit) FROM visit_spacial ORDER BY 1")
            days = [row[0] for row in self.cursor.fetchall()]
            return {'years': years, 'months': months, 'days': days}
        except Exception as e:
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาด : {e}')
            return False
        finally:
            self.close()

    # ตารางเยี่ยมพิเศษ ดึงข้อมูลการเยี่ยมรอบพิเศษ
    @require_valid_key
    def get_visits_on_visit_spacial(self,data_visit):
        self.connect()
        try:
            self.cursor.execute('''
                                SELECT
                                    visit_spacial.visit_id,
                                    visit_spacial.time_stamp,
                                    visit_spacial.date_visit,
                                    visit_spacial.time_visit,
                                    prisoners_.f_name || " " || prisoners_.l_name AS prisoner_name,
                                    prisoners_.dan,
                                    COALESCE(r1.title || " " || r1.f_name || " " || r1.l_name, '-') AS relative_1,
                                    COALESCE(r2.title || " " || r2.f_name || " " || r2.l_name, '-') AS relative_2,
                                    COALESCE(r3.title || " " || r3.f_name || " " || r3.l_name, '-') AS relative_3,
                                    COALESCE(r4.title || " " || r4.f_name || " " || r4.l_name, '-') AS relative_4,
                                    COALESCE(r5.title || " " || r5.f_name || " " || r5.l_name, '-') AS relative_5,
                                    visit_spacial.channel
                                FROM
                                    visit_spacial
                                JOIN prisoners_ ON visit_spacial.prisoner_id = prisoners_.prisoner_id
                                LEFT JOIN relatives AS r1 ON visit_spacial.relative_id_1 = r1.relative_id
                                LEFT JOIN relatives AS r2 ON visit_spacial.relative_id_2 = r2.relative_id
                                LEFT JOIN relatives AS r3 ON visit_spacial.relative_id_3 = r3.relative_id
                                LEFT JOIN relatives AS r4 ON visit_spacial.relative_id_4 = r4.relative_id
                                LEFT JOIN relatives AS r5 ON visit_spacial.relative_id_5 = r5.relative_id
                                WHERE 
                                    visit_spacial.date_visit = ? AND visit_spacial.time_visit = ? ''',
                                    (data_visit[0],data_visit[1])
                                )
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
            self.msgbox(e)
            return False
        finally:
            self.close()

    # รตารางเยี่ยมพิเศษ ค้นหาทั้งหมด
    @require_valid_key
    def get_visit_all_on_visit_spacial(self,round_date):
        self.connect()
        try:
            self.cursor.execute('''
                                SELECT
                                    visit_spacial.visit_id,
                                    visit_spacial.time_stamp,
                                    visit_spacial.date_visit,
                                    visit_spacial.time_visit,
                                    prisoners_.f_name || " " || prisoners_.l_name AS prisoner_name,
                                    COALESCE(r1.title || " " || r1.f_name || " " || r1.l_name, '-') AS relative_1,
                                    COALESCE(r2.title || " " || r2.f_name || " " || r2.l_name, '-') AS relative_2,
                                    COALESCE(r3.title || " " || r3.f_name || " " || r3.l_name, '-') AS relative_3,
                                    COALESCE(r4.title || " " || r4.f_name || " " || r4.l_name, '-') AS relative_4,
                                    COALESCE(r5.title || " " || r5.f_name || " " || r5.l_name, '-') AS relative_5,
                                    visit_spacial.channel
                                FROM
                                    visit_spacial
                                JOIN prisoners_ ON visit_spacial.prisoner_id = prisoners_.prisoner_id
                                LEFT JOIN relatives AS r1 ON visit_spacial.relative_id_1 = r1.relative_id
                                LEFT JOIN relatives AS r2 ON visit_spacial.relative_id_2 = r2.relative_id
                                LEFT JOIN relatives AS r3 ON visit_spacial.relative_id_3 = r3.relative_id
                                LEFT JOIN relatives AS r4 ON visit_spacial.relative_id_4 = r4.relative_id
                                LEFT JOIN relatives AS r5 ON visit_spacial.relative_id_5 = r5.relative_id
                                WHERE 
                                    visit_spacial.date_visit = ?''',
                                    (round_date,)
                                )
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
            self.msgbox(e)
            return False
        finally:
            self.close()


    # เพิ่มข้อมูลผู้ต้องขังใส่ตาราง prisoners_
    @require_valid_key
    def add_data(self,data):
        self.connect()
        try :
            # print('กำลังบันทึกข้อมูล')
            self.cursor.execute('INSERT INTO prisoners_ (prisoner_id,sex,f_name,l_name,lawsuit,level,dan,type,status) VALUES (?,?,?,?,?,?,?,?,?)',data)
            return True
        except Exception as e:
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
            # ตรวจสอบว่า relative_id มีอยู่แล้วหรือไม่
            self.cursor.execute('SELECT COUNT(*) FROM relatives WHERE relative_id = ?', (data[0],))
            if self.cursor.fetchone()[0] > 0:
                # relative_id นี้มีอยู่แล้ว
                print('ข้อมูลซ้ำ: relative_id นี้มีอยู่แล้ว')
                return False
            # บันทึกข้อมูล ในตารางญาติ
            self.cursor.execute(
                'INSERT INTO relatives (relative_id, title, f_name, l_name, address, tel) VALUES (?, ?, ?, ?, ?, ?)',
                (data[0], data[1], data[2], data[3], data[4], data[5])
            )
            return True
        except Exception as e:
            import sys
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name, str(e)])
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
            # print('เชื่อมข้อมูลระหว่าง prisoner_id และ relative_id และระบุความสัมพันธ์')
            return True
        except Exception as e:
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
            print(e)
            return False
        finally:
            self.close()
            self.encode_db()

    # ดึงข้อมูลผู้ต้องขังใส่ตาราง prisoners_ 
    @require_valid_key
    def get_data_all(self):
        self.decode_db()
        self.connect()
        try:
            if self.cursor is None:
                print("Error: Database cursor is None")
                return []
                
            self.cursor.execute('SELECT prisoner_id,sex,f_name,l_name,lawsuit,level,dan,type,status,disciplinary FROM prisoners_')
            self.all_data = self.cursor.fetchall()
            return [[value if value is not None else "" for value in row] for row in self.all_data]
        except Exception as e:
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาด {e}')
            return []
        finally:
            self.close()
            self.encode_db()

    @require_valid_key
    def get_join_tabel_print_recipt(self,id):
        '''
        data[0] = ชื่อ ผตข *
        data[1] = นามสกุล ผตช*
            data[2] = ชั้น   
            data[3] = แดน
        data[2] = วันที่*
        data[3] = เวลาเยี่ยม 10:00:00*
        data[4] = ช่องเยี่ยม*
        data[5] = สิทธิ์การเยี่ยมคงเหลือ เดือน ... ครั้ง ...
        data[6] = รายชื่อเข้าเยี่ยม
        '''
        def get_thai_month(date_str):
            thai_months = [
                "", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
                "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
            ]
            month = int(date_str.split("-")[1])
            return thai_months[month]
        def date_to_thai(date_str):
            thai_months = [
                "", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
                "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
            ]
            thai_days = [
                "วันจันทร์", "วันอังคาร", "วันพุธ", "วันพฤหัสบดี", "วันศุกร์", "วันเสาร์", "วันอาทิตย์"
            ]
            year, month, day = map(int, date_str.split("-"))
            dt = datetime.date(year, month, day)
            day_name = thai_days[dt.weekday()]  # weekday(): 0=Monday ... 6=Sunday
            month_th = thai_months[month]
            year_th = year + 543
            return f"{day_name} ที่ {day} {month_th} {year_th}"
        self.connect()
        try:
            self.cursor.execute('SELECT date_visit,time_visit,prisoner_id,relative_id_1,relative_id_2,relative_id_3,relative_id_4,relative_id_5,channel FROM visits WHERE visit_id = ?',(id,))
            data = self.cursor.fetchone()
            date = data[0]
            time = data[1]
            prisoner_id = data[2]
            channel = data[8]
            relative_ids = [v for v in data[2:8] if v is not None]
            placeholders = ','.join(['?'] * len(relative_ids))
            sql = f'''
                SELECT 
                    p.f_name,
                    p.l_name,
                    p.level,
                    p.dan,
                    r.f_name,
                    r.l_name
                FROM relations rel
                JOIN prisoners_ p ON rel.prisoner_id = p.prisoner_id
                JOIN relatives r ON rel.relative_id = r.relative_id
                WHERE rel.prisoner_id = ?
                AND rel.relative_id IN ({placeholders})
            '''
            params = [prisoner_id] + relative_ids
            self.cursor.execute(sql, params)
            result = self.cursor.fetchall()
            prisoner_fname = result[0][0] if result else ""
            prisoner_lname = result[0][1] if result else ""
            level = result[0][2]
            dan = result[0][3]
            relatives_names = [f"{row[4]} {row[5]}" for row in result]
            check_visit = self.get_count_visit(prisoner_id,date,date[:7])
            count_reserve = check_visit[1]
            if level == 'เยี่ยม' :
                count_reserve = 8 - count_reserve
            if level == 'ดีมาก' :
                count_reserve = 6 - count_reserve
            if level == 'ดี' :
                count_reserve = 4 - count_reserve
            if level == 'กลาง' or level == 'ระหว่างพิจารณาคดี' :
                count_reserve = 3 - count_reserve
            if level == 'ปรับปรุง' :
                count_reserve = 2 - count_reserve
            if level == 'ปรับปรุงมาก' :
                count_reserve = 1 - count_reserve
            month = get_thai_month(date)
            thai_date = date_to_thai(date)
            return [prisoner_fname, prisoner_lname, level, dan] + [thai_date] + [time] + [channel] + [f'สิทธิ์การเยี่ยมคงเหลือ เดือน {month} เหลือ {count_reserve} ครั้ง'] + relatives_names
        except Exception as e:
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาด : {e}')
            return False
        finally:
            self.close()

    # ดึงข้อมูลผู้ต้องขัง 1 คน ในตาราง prisoners_ ด้วย prisoner_id
    @require_valid_key
    def get_data_one(self,prisoner_id):
        self.decode_db()
        self.connect()
        try:
            self.cursor.execute('SELECT * FROM prisoners_ WHERE prisoner_id = ?',(prisoner_id,))
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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
        '''
        ดึงตารางข้อมูลผู้ต้องขัง อ้างอิงด้วย เลขบัตรประชาชนญาติ
        '''
        self.decode_db()
        self.connect()
        try:
            self.cursor.execute('''
                                SELECT 
                                    prisoners_.prisoner_id,
                                    prisoners_.f_name,
                                    prisoners_.l_name,
                                    prisoners_.level,
                                    prisoners_.dan,
                                    relations.relation,
                                    prisoners_.status,
                                    prisoners_.type
                                FROM prisoners_ 
                                JOIN relations ON prisoners_.prisoner_id = relations.prisoner_id
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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาด : {e}')
            return False
        finally:
            self.close()
            self.encode_db()

    # เพิ่มข้อมูลการเยี่ยมลงตาราง visit
    @require_valid_key
    def add_visits(self,query,data):
        self.connect()
        try:
            self.cursor.execute(query,data)
            return True
        except Exception as e:
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
            self.msgbox(e)
            return False
        finally:
            self.close()

    # รายงานการเยี่ยมประจำวัน ค้นหาทั้งหมด
    @require_valid_key
    def get_visits_all_on_db(self):
        self.connect()
        try:
            self.cursor.execute('''
                                SELECT
                                    visits.visit_id,
                                    visits.time_stamp,
                                    visits.date_visit,
                                    visits.time_visit,
                                    prisoners_.f_name || " " || prisoners_.l_name AS prisoner_name,
                                    COALESCE(r1.title || " " || r1.f_name || " " || r1.l_name, '-') AS relative_1,
                                    COALESCE(r2.title || " " || r2.f_name || " " || r2.l_name, '-') AS relative_2,
                                    COALESCE(r3.title || " " || r3.f_name || " " || r3.l_name, '-') AS relative_3,
                                    COALESCE(r4.title || " " || r4.f_name || " " || r4.l_name, '-') AS relative_4,
                                    COALESCE(r5.title || " " || r5.f_name || " " || r5.l_name, '-') AS relative_5,
                                    visits.channel
                                FROM
                                    visits
                                JOIN prisoners_ ON visits.prisoner_id = prisoners_.prisoner_id
                                LEFT JOIN relatives AS r1 ON visits.relative_id_1 = r1.relative_id
                                LEFT JOIN relatives AS r2 ON visits.relative_id_2 = r2.relative_id
                                LEFT JOIN relatives AS r3 ON visits.relative_id_3 = r3.relative_id
                                LEFT JOIN relatives AS r4 ON visits.relative_id_4 = r4.relative_id
                                LEFT JOIN relatives AS r5 ON visits.relative_id_5 = r5.relative_id
                                WHERE 
                                    visits.date_visit = ?''',
                                    (TODAYS_STR,)
                                )
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
                                    prisoners_.f_name || " " || prisoners_.l_name AS prisoner_name,
                                    prisoners_.dan,
                                    COALESCE(r1.title || " " || r1.f_name || " " || r1.l_name, '-') AS relative_1,
                                    COALESCE(r2.title || " " || r2.f_name || " " || r2.l_name, '-') AS relative_2,
                                    COALESCE(r3.title || " " || r3.f_name || " " || r3.l_name, '-') AS relative_3,
                                    COALESCE(r4.title || " " || r4.f_name || " " || r4.l_name, '-') AS relative_4,
                                    COALESCE(r5.title || " " || r5.f_name || " " || r5.l_name, '-') AS relative_5,
                                    visits.channel
                                FROM
                                    visits
                                JOIN prisoners_ ON visits.prisoner_id = prisoners_.prisoner_id
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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
                                    prisoners_.f_name || " " || prisoners_.l_name AS prisoner_name,
                                    COALESCE(r1.title || " " || r1.f_name || " " || r1.l_name, '-') AS relative_1,
                                    COALESCE(r2.title || " " || r2.f_name || " " || r2.l_name, '-') AS relative_2,
                                    COALESCE(r3.title || " " || r3.f_name || " " || r3.l_name, '-') AS relative_3,
                                    COALESCE(r4.title || " " || r4.f_name || " " || r4.l_name, '-') AS relative_4,
                                    COALESCE(r5.title || " " || r5.f_name || " " || r5.l_name, '-') AS relative_5,
                                    visits.channel
                                FROM
                                    visits
                                JOIN prisoners_ ON visits.prisoner_id = prisoners_.prisoner_id
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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
        # print(round_time,date_current)

        try:
            self.cursor.execute('SELECT count (*) FROM visits WHERE time_visit = ? AND date_visit = ?',(round_time,date_current))
            count = self.cursor.fetchone()[0]
            return count
        except Exception as e:
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
            # print(id,level,dan,type_data,status,disciplinary)
            self.cursor.execute('''UPDATE 
                                    prisoners_ 
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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาดใน get_all_relatives: {e}')
            return []
        finally:
            self.close()

    # ลบข้อมูลญาติ
    @require_valid_key
    def delete_relation_from_prisoner_and_relative(self,prisoner_id,relative_id):
        # print(prisoner_id,relative_id)
        self.connect()
        try:
            self.cursor.execute('DELETE FROM relations WHERE prisoner_id = ? AND relative_id = ?',(prisoner_id,relative_id))
            return True
        except Exception as e:
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
            self.msgbox(e)
            return False
        finally:
            self.close()

    # ลบข้อมูลผู้ต้องขัง
    @require_valid_key
    def delete_prisoner(self,id):
        self.connect()
        try:
            # print(type(id))
            self.cursor.execute('DELETE FROM prisoners_ WHERE prisoner_id = ?',(id,))
            return True
        except Exception as e:
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
            self.msgbox(e)
            print(e)
            return False
        finally:
            self.close()
            
    # ย้ายรอบเยี่ยม
    @require_valid_key
    def update_visit_round_and_channel(self,new_round,new_channel,visit_id):
        self.connect()
        try:
            self.cursor.execute('UPDATE visits SET time_visit = ?, channel = ? WHERE visit_id = ?',(new_round,new_channel,visit_id))
            return True
        except Exception as e:
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
            print(e)
            self.msgbox(e)
            return False
        finally:
            self.close()

    # ดึงข้อมูลตารางเยี่ยม โดยใช้ visit_id
    @require_valid_key
    def prisoner_id_on_table_visits(self,visit_id):
        # print(f'visit_id on db = {visit_id}')
        self.connect()
        try:
            self.cursor.execute('SELECT prisoner_id FROM visits WHERE visit_id = ?',(visit_id,))
            data = self.cursor.fetchone()[0]
            return data
        except Exception as e:
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาด : {e}')
            return False
        finally:
            self.close()

    @require_valid_key
    def get_channel(self,date,round_time):
        self.connect()
        try:
            self.cursor.execute('SELECT channel FROM visits WHERE date_visit = ? AND time_visit = ?',(date,round_time))
            data = [row[0] for row in self.cursor.fetchall() if row[0] is not None]
            return data
        except Exception as e:
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาด : {e}')
            return False
        finally:
            self.close()

    @require_valid_key
    def update_channel(self,channel,visit_id):
        self.connect()
        try:
            self.cursor.execute('UPDATE visits SET channel = ? WHERE visit_id = ?',(channel,visit_id))
            return True
        except Exception as e:
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
            self.msgbox(e)
            print(f'เกิดข้อผิดพลาด : {e}')
            return False
        finally:
            self.close()

    # ดึงข้อมูลวันหยุด
    def get_holidays(self):
        self.connect()
        try:
            self.cursor.execute('SELECT date FROM holidays')
            return self.cursor.fetchall()
        except Exception as e:
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
            import sys
            func_name = sys._getframe().f_code.co_name # หรือใส่ชื่อฟังก์ชันเองเป็น string ก็ได้
            self.log_error([func_name,str(e)])
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
