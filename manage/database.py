import os
import sys
from manage.encryption_utils import decrypt_file, encrypt_file
from tkinter import messagebox
import json
from pathlib import Path
import tempfile
import datetime
import psycopg2
from psycopg2 import Binary
from psycopg2 import errors
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
    try:
        with psycopg2.connect(**connection_params) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute('SELECT key FROM check_')
                result = cur.fetchone()
                return result[0] if result else None
    except Exception as e:
        print(f"Error checking key: {e}")
        return None

def require_valid_key(func):
    KEY = 'E54F2JN5FO'
    def wrapper(self, *args, **kwargs):
        KEY_DB = check_key_on_db()  # <-- เรียกทุกครั้งที่ใช้งาน
        if KEY_DB != KEY:
            messagebox.showerror("แจ้งอัพเดท","กรุณาอัพเดทโปรแกรม")
            raise PermissionError("KEY ไม่ถูกต้อง ไม่สามารถใช้งาน method นี้ได้")
        return func(self, *args, **kwargs)
    return wrapper

class SQLiteDB: # เปลี่ยนชื่อคลาสหรือจะใช้ SQLiteDB ชื่อเดิมก็ได้เพื่อให้โปรแกรมเดิมทำงานต่อได้
    def __init__(self, db_path=None):
        # ใน Postgres ไม่ใช้ db_path แต่คงรับค่าไว้เผื่อโครงสร้างเดิมส่งมา
        self.conn = None
        self.cursor = None
        self.create_table()
        self.key = self.check_key()

    def connect(self):
        try:
            connection_params = {
                'host': os.getenv("PG_HOST"),
                'port': os.getenv("PG_PORT"),
                'dbname': os.getenv("PG_NAME"),
                'user': os.getenv("PG_USER"),
                'password': os.getenv("PG_PASS")
            }
            self.conn = psycopg2.connect(**connection_params)
            self.conn.autocommit = False # เพื่อให้เราควบคุมการ commit เอง
            self.cursor = self.conn.cursor()
            return True
        except psycopg2.Error as e:
            func_name = sys._getframe().f_code.co_name
            print(f"Database connection error: {e}")
            messagebox.showerror('เชื่อมต่อฐานข้อมูลไม่สำเร็จ',str(e))
            self.conn = None
            self.cursor = None
            return False

    def close(self):
        if self.conn:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()
            self.conn = None
            self.cursor = None

    def msgbox(self,e):
        messagebox.showerror('ฐานข้อมูล',f'{e}')

    def create_table(self):
        def visit_spacial_table():
            if not self.connect(): return False
            try:
                self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS "visit_spacial" (
                        "visit_id" SERIAL PRIMARY KEY,
                        "time_stamp" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        "date_visit" TEXT NOT NULL,
                        "time_visit" TEXT NOT NULL,
                        "prisoner_id" BIGINT NOT NULL,
                        "relative_id_1" BIGINT,
                        "relative_id_2" BIGINT,
                        "relative_id_3" BIGINT,
                        "relative_id_4" BIGINT,
                        "relative_id_5" BIGINT,
                        "channel" INTEGER
                    )
                ''')
                return True
            except Exception as e:
                self.conn.rollback()
                func_name = sys._getframe().f_code.co_name
                print(f'ข้อผิดพลาด: {e}')
                return False
            finally:
                self.close()

        def log_error():
            if not self.connect(): return False
            try:
                self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS "log_error" (
                        log_id SERIAL PRIMARY KEY,
                        time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        function_name TEXT,
                        error_message TEXT,
                        extra_info TEXT
                    )
                ''')
                return True
            except Exception as e:
                self.conn.rollback()
                func_name = sys._getframe().f_code.co_name
                print(f'ข้อผิดพลาด: {e}')
                return False
            finally:
                self.close()
        
        def create_all_tables():
            if not self.connect(): return False
            try:
                self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS "prisoners_" (
                        "prisoner_id" BIGINT PRIMARY KEY,
                        "sex" TEXT NOT NULL,
                        "f_name" TEXT NOT NULL,
                        "l_name" TEXT NOT NULL,
                        "lawsuit" TEXT NOT NULL,
                        "level" TEXT NOT NULL,
                        "dan" TEXT NOT NULL,
                        "type" TEXT,
                        "status" TEXT,
                        "disciplinary" TEXT
                    )
                ''')

                self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS "relatives" (
                        "relative_id" BIGINT PRIMARY KEY,
                        "title" TEXT NOT NULL,
                        "f_name" TEXT NOT NULL,
                        "l_name" TEXT NOT NULL,
                        "address" TEXT NOT NULL,
                        "tel" TEXT NOT NULL,
                        "fingerprint" BYTEA
                    )
                ''')

                self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS "relations" (
                        "id" SERIAL PRIMARY KEY,
                        "prisoner_id" BIGINT NOT NULL,
                        "relative_id" BIGINT NOT NULL,
                        "relation" TEXT NOT NULL
                    )
                ''')

                self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS "visits" (
                        "visit_id" SERIAL PRIMARY KEY,
                        "time_stamp" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        "date_visit" TEXT NOT NULL,
                        "time_visit" TEXT NOT NULL,
                        "prisoner_id" BIGINT NOT NULL,
                        "relative_id_1" BIGINT,
                        "relative_id_2" BIGINT,
                        "relative_id_3" BIGINT,
                        "relative_id_4" BIGINT,
                        "relative_id_5" BIGINT,
                        "channel" INTEGER
                    )
                ''')
                return True
            except Exception as e:
                self.conn.rollback()
                func_name = sys._getframe().f_code.co_name
                print(f"เกิดข้อผิดพลาดในการสร้างตาราง: {e}")
                return False
            finally:
                self.close()

        visit_spacial_table()
        log_error()
        create_all_tables()

    def check_key(self):
        self.connect()
        try:
            self.cursor.execute('SELECT key FROM check_')
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            print(f'เกิดข้อผิดพลาด : {e}')
            return False
        finally:
            self.close()

    def get_dashboard_summary(self,date_str):
        self.connect()
        try:
            self.cursor.execute("SELECT COUNT(*) FROM prisoners WHERE status = 'อยู่' AND type = 'ผู้ต้องขัง'")
            prisoner_normal = self.cursor.fetchone()[0]

            self.cursor.execute("SELECT COUNT(*) FROM prisoners WHERE status = 'อยู่' AND sex = 'ชาย' AND type = 'ผู้ต้องขัง'")
            prisoner_male = self.cursor.fetchone()[0]

            self.cursor.execute("SELECT COUNT(*) FROM prisoners WHERE status = 'อยู่' AND sex = 'หญิง' AND type = 'ผู้ต้องขัง'")
            prisoner_female = self.cursor.fetchone()[0]

            self.cursor.execute("SELECT COUNT(*) FROM prisoners WHERE type = 'ผู้ต้องกักขัง' AND status = 'อยู่'")
            prisoner_detained = self.cursor.fetchone()[0]

            self.cursor.execute("SELECT COUNT(*) FROM prisoners WHERE type = 'ผู้ต้องกักขัง' AND status = 'อยู่' AND sex = 'ชาย'")
            detained_male = self.cursor.fetchone()[0]

            self.cursor.execute("SELECT COUNT(*) FROM prisoners WHERE type = 'ผู้ต้องกักขัง' AND status = 'อยู่' AND sex = 'หญิง'")
            detained_female = self.cursor.fetchone()[0]

            self.cursor.execute("SELECT COUNT(*) FROM prisoners WHERE disciplinary = 'ผิดวินัย' AND status = 'อยู่'")
            prisoner_disciplinary = self.cursor.fetchone()[0]

            self.cursor.execute("SELECT COUNT(*) FROM prisoners WHERE disciplinary = 'ผิดวินัย' AND status = 'อยู่' AND sex = 'ชาย'")
            prisoner_disciplinary_male = self.cursor.fetchone()[0]            
            
            self.cursor.execute("SELECT COUNT(*) FROM prisoners WHERE disciplinary = 'ผิดวินัย' AND status = 'อยู่' AND sex = 'หญิง'")
            prisoner_disciplinary_female = self.cursor.fetchone()[0]

            self.cursor.execute("SELECT COUNT(*) FROM relatives")
            relatives_total = self.cursor.fetchone()[0]

            self.cursor.execute("SELECT COUNT(*) FROM relatives WHERE title IN ('นาย','ด.ช.','เด็กชาย','พระ')")
            relatives_male = self.cursor.fetchone()[0]            
            
            self.cursor.execute("SELECT COUNT(*) FROM relatives WHERE title IN ('นาง','น.ส.','นางสาว','ด.ญ.','เด็กหญิง')")
            relatives_female = self.cursor.fetchone()[0]

            self.cursor.execute("SELECT COUNT(DISTINCT prisoner_id) FROM visits WHERE date_visit = %s",(date_str,))
            prisoner_visited_today = self.cursor.fetchone()[0]

            self.cursor.execute("""
                SELECT COUNT(*) FROM (
                    SELECT relative_id_1 AS rid FROM visits WHERE date_visit = %s AND relative_id_1 IS NOT NULL
                    UNION ALL SELECT relative_id_2 FROM visits WHERE date_visit = %s AND relative_id_2 IS NOT NULL
                    UNION ALL SELECT relative_id_3 FROM visits WHERE date_visit = %s AND relative_id_3 IS NOT NULL
                    UNION ALL SELECT relative_id_4 FROM visits WHERE date_visit = %s AND relative_id_4 IS NOT NULL
                    UNION ALL SELECT relative_id_5 FROM visits WHERE date_visit = %s AND relative_id_5 IS NOT NULL
                ) sub WHERE rid IS NOT NULL
            """, (date_str, date_str, date_str, date_str, date_str))
            relatives_visited_today = self.cursor.fetchone()[0]

            self.cursor.execute("""
                SELECT COUNT(*) FROM (
                    SELECT r.title
                    FROM (
                        SELECT relative_id_1 AS rid FROM visits WHERE date_visit = %s AND relative_id_1 IS NOT NULL
                        UNION ALL SELECT relative_id_2 FROM visits WHERE date_visit = %s AND relative_id_2 IS NOT NULL
                        UNION ALL SELECT relative_id_3 FROM visits WHERE date_visit = %s AND relative_id_3 IS NOT NULL
                        UNION ALL SELECT relative_id_4 FROM visits WHERE date_visit = %s AND relative_id_4 IS NOT NULL
                        UNION ALL SELECT relative_id_5 FROM visits WHERE date_visit = %s AND relative_id_5 IS NOT NULL
                    ) v
                    JOIN relatives r ON v.rid = r.relative_id
                    WHERE r.title IN ('นาย','ด.ช.','เด็กชาย','พระ')
                ) sub
            """, (date_str, date_str, date_str, date_str, date_str))
            relatives_visited_male_today = self.cursor.fetchone()[0]

            self.cursor.execute("""
                SELECT COUNT(*) FROM (
                    SELECT r.title
                    FROM (
                        SELECT relative_id_1 AS rid FROM visits WHERE date_visit = %s AND relative_id_1 IS NOT NULL
                        UNION ALL SELECT relative_id_2 FROM visits WHERE date_visit = %s AND relative_id_2 IS NOT NULL
                        UNION ALL SELECT relative_id_3 FROM visits WHERE date_visit = %s AND relative_id_3 IS NOT NULL
                        UNION ALL SELECT relative_id_4 FROM visits WHERE date_visit = %s AND relative_id_4 IS NOT NULL
                        UNION ALL SELECT relative_id_5 FROM visits WHERE date_visit = %s AND relative_id_5 IS NOT NULL
                    ) v
                    JOIN relatives r ON v.rid = r.relative_id
                    WHERE r.title IN ('นาง','น.ส.','นางสาว','ด.ญ.','เด็กหญิง')
                ) sub
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
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name, str(e)])
            print(f'เกิดข้อผิดพลาด : {e}')
            return None
        finally:
            self.close()

    def log_error(self,log_data):
        self.connect()
        try:
            data = list(log_data) + [None] * (3 - len(log_data))
            self.cursor.execute(
                'INSERT INTO log_error (function_name, error_message, extra_info) VALUES (%s, %s, %s)',
                data[:3]
            )
            return True
        except Exception as e:
            self.conn.rollback()
            print(f'เกิดข้อผิดพลาดในการบันทึก Log : {e}')
            return False
        finally:
            self.close()

    def get_log(self):
        self.connect()
        try:
            self.cursor.execute('SELECT * FROM log_error ORDER BY time_stamp DESC')
            return self.cursor.fetchall()    
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def get_chanel_on_visit_spacial(self,time_,date_):
        self.connect()
        try:
            self.cursor.execute('SELECT count(*) FROM visit_spacial WHERE time_visit = %s AND date_visit = %s',(time_,date_))
            count = self.cursor.fetchone()[0]
            return count      
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def check_visit_spacial_log(self,prisoner_id,date):
        self.connect()
        try:
            self.cursor.execute('SELECT count(*) FROM visit_spacial WHERE prisoner_id = %s AND date_visit = %s',(prisoner_id,date))
            count = self.cursor.fetchone()[0]
            return count      
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def add_visit_to_visit_spacial(self,query,data):
        self.connect()
        try:
            query = query.replace('?', '%s')
            self.cursor.execute(query,data)
            return True
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def get_chanel_blank_on_visit_spacial(self,time,date):
        self.connect()
        try:
            self.cursor.execute('SELECT channel FROM visit_spacial WHERE date_visit = %s AND time_visit = %s',(date,time))
            data = [row[0] for row in self.cursor.fetchall() if row[0] is not None]
            return data
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def get_date_on_visit_spacial(self):
        self.connect()
        try:
            self.cursor.execute("SELECT DISTINCT TO_CHAR(CAST(date_visit AS DATE), 'YYYY') FROM visit_spacial ORDER BY 1")
            years = [row[0] for row in self.cursor.fetchall()]
            self.cursor.execute("SELECT DISTINCT TO_CHAR(CAST(date_visit AS DATE), 'MM') FROM visit_spacial ORDER BY 1")
            months = [row[0] for row in self.cursor.fetchall()]
            self.cursor.execute("SELECT DISTINCT TO_CHAR(CAST(date_visit AS DATE), 'DD') FROM visit_spacial ORDER BY 1")
            days = [row[0] for row in self.cursor.fetchall()]
            return {'years': years, 'months': months, 'days': days}
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

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
                    prisoners.f_name || ' ' || prisoners.l_name AS prisoner_name,
                    prisoners.dan,
                    COALESCE(r1.title || ' ' || r1.f_name || ' ' || r1.l_name, '-') AS relative_1,
                    COALESCE(r2.title || ' ' || r2.f_name || ' ' || r2.l_name, '-') AS relative_2,
                    COALESCE(r3.title || ' ' || r3.f_name || ' ' || r3.l_name, '-') AS relative_3,
                    COALESCE(r4.title || ' ' || r4.f_name || ' ' || r4.l_name, '-') AS relative_4,
                    COALESCE(r5.title || ' ' || r5.f_name || ' ' || r5.l_name, '-') AS relative_5,
                    visit_spacial.channel
                FROM visit_spacial
                JOIN prisoners ON visit_spacial.prisoner_id = prisoners.prisoner_id
                LEFT JOIN relatives AS r1 ON visit_spacial.relative_id_1 = r1.relative_id
                LEFT JOIN relatives AS r2 ON visit_spacial.relative_id_2 = r2.relative_id
                LEFT JOIN relatives AS r3 ON visit_spacial.relative_id_3 = r3.relative_id
                LEFT JOIN relatives AS r4 ON visit_spacial.relative_id_4 = r4.relative_id
                LEFT JOIN relatives AS r5 ON visit_spacial.relative_id_5 = r5.relative_id
                WHERE visit_spacial.date_visit = %s AND visit_spacial.time_visit = %s ''',
                (data_visit[0],data_visit[1])
            )
            return self.cursor.fetchall()
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

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
                    prisoners.f_name || ' ' || prisoners.l_name AS prisoner_name,
                    COALESCE(r1.title || ' ' || r1.f_name || ' ' || r1.l_name, '-') AS relative_1,
                    COALESCE(r2.title || ' ' || r2.f_name || ' ' || r2.l_name, '-') AS relative_2,
                    COALESCE(r3.title || ' ' || r3.f_name || ' ' || r3.l_name, '-') AS relative_3,
                    COALESCE(r4.title || ' ' || r4.f_name || ' ' || r4.l_name, '-') AS relative_4,
                    COALESCE(r5.title || ' ' || r5.f_name || ' ' || r5.l_name, '-') AS relative_5,
                    visit_spacial.channel
                FROM visit_spacial
                JOIN prisoners ON visit_spacial.prisoner_id = prisoners.prisoner_id
                LEFT JOIN relatives AS r1 ON visit_spacial.relative_id_1 = r1.relative_id
                LEFT JOIN relatives AS r2 ON visit_spacial.relative_id_2 = r2.relative_id
                LEFT JOIN relatives AS r3 ON visit_spacial.relative_id_3 = r3.relative_id
                LEFT JOIN relatives AS r4 ON visit_spacial.relative_id_4 = r4.relative_id
                LEFT JOIN relatives AS r5 ON visit_spacial.relative_id_5 = r5.relative_id
                WHERE visit_spacial.date_visit = %s''',
                (round_date,)
            )
            return self.cursor.fetchall()
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def add_data(self,data):
        self.connect()
        try :
            self.cursor.execute('''
                INSERT INTO prisoners 
                (prisoner_id,sex,f_name,l_name,lawsuit,level,dan,type,status) 
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ''', data)
            return True
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def add_data_ralative_to_relatives(self,id,data,relation):
        self.connect()
        try:
            self.cursor.execute('SELECT COUNT(*) FROM relatives WHERE relative_id = %s', (data[0],))
            if self.cursor.fetchone()[0] > 0:
                print('ข้อมูลซ้ำ: relative_id นี้มีอยู่แล้ว')
                return False
            self.cursor.execute(
                'INSERT INTO relatives (relative_id, title, f_name, l_name, address, tel) VALUES (%s, %s, %s, %s, %s, %s)',
                (data[0], data[1], data[2], data[3], data[4], data[5])
            )
            return True
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name, str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def add_data_relation_to_ralations(self,id,data,relation):
        self.connect()
        try:
            self.cursor.execute('INSERT INTO relations (prisoner_id,relative_id,relation) VALUES (%s,%s,%s)',(id,data[0],relation))
            return True
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def get_data_all(self):
        self.connect()
        try:
            self.cursor.execute('SELECT prisoner_id,sex,f_name,l_name,lawsuit,level,dan,type,status,disciplinary FROM prisoners')
            self.all_data = self.cursor.fetchall()
            return [[value if value is not None else "" for value in row] for row in self.all_data]
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return []
        finally:
            self.close()

    @require_valid_key
    def get_join_tabel_print_recipt(self,id):
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
            day_name = thai_days[dt.weekday()]
            month_th = thai_months[month]
            year_th = year + 543
            return f"{day_name} ที่ {day} {month_th} {year_th}"
            
        self.connect()
        try:
            self.cursor.execute('SELECT date_visit,time_visit,prisoner_id,relative_id_1,relative_id_2,relative_id_3,relative_id_4,relative_id_5,channel FROM visits WHERE visit_id = %s',(id,))
            data = self.cursor.fetchone()
            date = data[0]
            time = data[1]
            prisoner_id = data[2]
            channel = data[8]
            relative_ids = [v for v in data[2:8] if v is not None]
            placeholders = ','.join(['%s'] * len(relative_ids))
            
            sql_query = f'''
                SELECT 
                    p.f_name,
                    p.l_name,
                    p.level,
                    p.dan,
                    r.f_name,
                    r.l_name
                FROM relations rel
                JOIN prisoners p ON rel.prisoner_id = p.prisoner_id
                JOIN relatives r ON rel.relative_id = r.relative_id
                WHERE rel.prisoner_id = %s
                AND rel.relative_id IN ({placeholders})
            '''
            params = [prisoner_id] + relative_ids
            self.cursor.execute(sql_query, params)
            result = self.cursor.fetchall()
            
            prisoner_fname = result[0][0] if result else ""
            prisoner_lname = result[0][1] if result else ""
            level = result[0][2]
            dan = result[0][3]
            relatives_names = [f"{row[4]} {row[5]}" for row in result]
            
            check_visit = self.get_count_visit(prisoner_id,date,date[:7])
            count_reserve = check_visit[1]
            if level == 'เยี่ยม' : count_reserve = 8 - count_reserve
            if level == 'ดีมาก' : count_reserve = 6 - count_reserve
            if level == 'ดี' : count_reserve = 4 - count_reserve
            if level == 'กลาง' or level == 'ระหว่างพิจารณาคดี' : count_reserve = 3 - count_reserve
            if level == 'ปรับปรุง' : count_reserve = 2 - count_reserve
            if level == 'ปรับปรุงมาก' : count_reserve = 1 - count_reserve
            
            month = get_thai_month(date)
            thai_date = date_to_thai(date)
            return [prisoner_fname, prisoner_lname, level, dan] + [thai_date] + [time] + [channel] + [f'สิทธิ์การเยี่ยมคงเหลือ เดือน {month} เหลือ {count_reserve} ครั้ง'] + relatives_names
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def get_data_one(self,prisoner_id):
        self.connect()
        try:
            self.cursor.execute('SELECT * FROM prisoners WHERE prisoner_id = %s',(prisoner_id,))
            return self.cursor.fetchone()
        except psycopg2.Error as e:
            self.conn.rollback()
            self.msgbox(e)
            return False
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def get_data_for_ralative_id(self,id):
        self.connect()
        try:
            self.cursor.execute('SELECT * FROM relatives WHERE relative_id = %s',(id,))
            return self.cursor.fetchone()
        except psycopg2.Error as e:
            self.conn.rollback()
            self.msgbox(e)
            return False
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def set_fingerprint(self,id,fingerprint):
        self.connect()
        try:
            # psycopg2 จัดการ binary data (BYTEA) ได้โดยตรง 
            self.cursor.execute('UPDATE relatives SET fingerprint = %s WHERE relative_id = %s',(fingerprint, id))
            return True
        except psycopg2.Error as e:
            self.conn.rollback()
            self.msgbox(e)
            return False
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

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
                WHERE rel.prisoner_id = %s
            ''',(prisoner_id,))
            return self.cursor.fetchall()
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

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
                WHERE relations.prisoner_id = %s AND NOT relations.relative_id = %s
            ''',(prisoner_id,national_id))
            return self.cursor.fetchall()
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def get_data_relation(self,prisoner_id):
        self.connect()
        try:
            self.cursor.execute('SELECT prisoner_id,relative_id FROM relations WHERE prisoner_id = %s',(prisoner_id,))
            return self.cursor.fetchall()
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()
    
    @require_valid_key
    def get_all_fingerprint(self):
        self.connect()
        try:
            self.cursor.execute('SELECT relative_id,title,f_name,l_name,fingerprint FROM relatives')
            return self.cursor.fetchall()
        finally:
            self.close()
    
    @require_valid_key
    def get_join_relatives_and_prisoners(self,relative_id):
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
                WHERE relations.relative_id = %s
            ''',(relative_id,))
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            self.conn.rollback()
            self.msgbox(e)
            return False
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def add_visits(self,query,data):
        self.connect()
        try:
            query = query.replace('?', '%s')
            self.cursor.execute(query,data)
            return True
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()
    
    @require_valid_key
    def add_channel_on_visits(self,data,channel):
        self.connect()
        try:
            self.cursor.execute('''
                UPDATE visits
                SET channel = %s
                WHERE date_visit = %s AND time_visit = %s AND prisoner_id = %s AND relative_id_1 = %s
            ''', (channel, data[0], data[1], data[2], data[3]))
            return True
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

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
                    prisoners.f_name || ' ' || prisoners.l_name AS prisoner_name,
                    COALESCE(r1.title || ' ' || r1.f_name || ' ' || r1.l_name, '-') AS relative_1,
                    COALESCE(r2.title || ' ' || r2.f_name || ' ' || r2.l_name, '-') AS relative_2,
                    COALESCE(r3.title || ' ' || r3.f_name || ' ' || r3.l_name, '-') AS relative_3,
                    COALESCE(r4.title || ' ' || r4.f_name || ' ' || r4.l_name, '-') AS relative_4,
                    COALESCE(r5.title || ' ' || r5.f_name || ' ' || r5.l_name, '-') AS relative_5,
                    visits.channel
                FROM visits
                JOIN prisoners ON visits.prisoner_id = prisoners.prisoner_id
                LEFT JOIN relatives AS r1 ON visits.relative_id_1 = r1.relative_id
                LEFT JOIN relatives AS r2 ON visits.relative_id_2 = r2.relative_id
                LEFT JOIN relatives AS r3 ON visits.relative_id_3 = r3.relative_id
                LEFT JOIN relatives AS r4 ON visits.relative_id_4 = r4.relative_id
                LEFT JOIN relatives AS r5 ON visits.relative_id_5 = r5.relative_id
                WHERE visits.date_visit = %s''',
                (TODAYS_STR,)
            )
            return self.cursor.fetchall()
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def get_visits_on_db(self,data_visit):
        self.connect()
        try:
            self.cursor.execute('''
                SELECT
                    visits.visit_id,
                    visits.time_stamp,
                    visits.date_visit,
                    visits.time_visit,
                    prisoners.f_name || ' ' || prisoners.l_name AS prisoner_name,
                    prisoners.dan,
                    COALESCE(r1.title || ' ' || r1.f_name || ' ' || r1.l_name, '-') AS relative_1,
                    COALESCE(r2.title || ' ' || r2.f_name || ' ' || r2.l_name, '-') AS relative_2,
                    COALESCE(r3.title || ' ' || r3.f_name || ' ' || r3.l_name, '-') AS relative_3,
                    COALESCE(r4.title || ' ' || r4.f_name || ' ' || r4.l_name, '-') AS relative_4,
                    COALESCE(r5.title || ' ' || r5.f_name || ' ' || r5.l_name, '-') AS relative_5,
                    visits.channel
                FROM visits
                JOIN prisoners ON visits.prisoner_id = prisoners.prisoner_id
                LEFT JOIN relatives AS r1 ON visits.relative_id_1 = r1.relative_id
                LEFT JOIN relatives AS r2 ON visits.relative_id_2 = r2.relative_id
                LEFT JOIN relatives AS r3 ON visits.relative_id_3 = r3.relative_id
                LEFT JOIN relatives AS r4 ON visits.relative_id_4 = r4.relative_id
                LEFT JOIN relatives AS r5 ON visits.relative_id_5 = r5.relative_id
                WHERE visits.date_visit = %s AND visits.time_visit = %s ''',
                (data_visit[0],data_visit[1])
            )
            return self.cursor.fetchall()
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def get_relatives_id_fname_lname(self):
        self.connect()
        try:
            self.cursor.execute('SELECT relative_id,f_name,l_name FROM relatives')
            return self.cursor.fetchall()
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()
            
    @require_valid_key
    def get_visits_by_month(self, data_month):
        self.connect()
        try:
            self.cursor.execute('''
                SELECT
                    visits.visit_id,
                    visits.time_stamp,
                    visits.date_visit,
                    visits.time_visit,
                    prisoners.f_name || ' ' || prisoners.l_name AS prisoner_name,
                    COALESCE(r1.title || ' ' || r1.f_name || ' ' || r1.l_name, '-') AS relative_1,
                    COALESCE(r2.title || ' ' || r2.f_name || ' ' || r2.l_name, '-') AS relative_2,
                    COALESCE(r3.title || ' ' || r3.f_name || ' ' || r3.l_name, '-') AS relative_3,
                    COALESCE(r4.title || ' ' || r4.f_name || ' ' || r4.l_name, '-') AS relative_4,
                    COALESCE(r5.title || ' ' || r5.f_name || ' ' || r5.l_name, '-') AS relative_5,
                    visits.channel
                FROM visits
                JOIN prisoners ON visits.prisoner_id = prisoners.prisoner_id
                LEFT JOIN relatives AS r1 ON visits.relative_id_1 = r1.relative_id
                LEFT JOIN relatives AS r2 ON visits.relative_id_2 = r2.relative_id
                LEFT JOIN relatives AS r3 ON visits.relative_id_3 = r3.relative_id
                LEFT JOIN relatives AS r4 ON visits.relative_id_4 = r4.relative_id
                LEFT JOIN relatives AS r5 ON visits.relative_id_5 = r5.relative_id
                WHERE TO_CHAR(CAST(visits.date_visit AS DATE), 'YYYY') = %s 
                  AND TO_CHAR(CAST(visits.date_visit AS DATE), 'MM') = %s
                ORDER BY visits.date_visit, visits.time_visit''',
                (data_month[0], data_month[1])
            )
            return self.cursor.fetchall()
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def get_relative_by_national_id(self,id):
        self.connect()
        try:
            self.cursor.execute('SELECT title,f_name,l_name FROM relatives WHERE relative_id = %s',(id,))
            return self.cursor.fetchall()
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def get_count_visit(self,prisoner_id,today,month):
        self.connect()
        try:
            self.cursor.execute('SELECT COUNT(*) FROM visits WHERE prisoner_id = %s AND date_visit = %s',(prisoner_id,today))
            count_today = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT COUNT(*) FROM visits WHERE prisoner_id = %s AND TO_CHAR(CAST(date_visit AS DATE), 'YYYY-MM') = %s",(prisoner_id,month))
            count_month = self.cursor.fetchone()[0]
            return count_today,count_month
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def get_count_visit_on_round(self,round_time,date_current):
        self.connect()
        try:
            self.cursor.execute('SELECT count(*) FROM visits WHERE time_visit = %s AND date_visit = %s',(round_time,date_current))
            count = self.cursor.fetchone()[0]
            return count
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def update_level_and_dan(self,id,sex,f_name,l_name,lawsuit,level,dan,type_data,status,disciplinary):
        self.connect()
        try:
            disciplinary_values = None if disciplinary == 'ไม่มี' else disciplinary
            self.cursor.execute('''
                UPDATE prisoners 
                SET sex = %s, f_name = %s, l_name = %s, lawsuit = %s, level = %s, 
                    dan = %s, type = %s, status = %s, disciplinary = %s
                WHERE prisoner_id = %s''',
                (sex,f_name,l_name,lawsuit,level,dan,type_data,status,disciplinary_values,id)
            )
            return True
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()    

    @require_valid_key
    def get_all_relatives(self):
        self.connect()
        try:
            self.cursor.execute('SELECT relative_id,title,f_name,l_name,address,tel FROM relatives')
            result = self.cursor.fetchall()
            return result if result else []
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return []
        finally:
            self.close()

    @require_valid_key
    def delete_relation_from_prisoner_and_relative(self,prisoner_id,relative_id):
        self.connect()
        try:
            self.cursor.execute('DELETE FROM relations WHERE prisoner_id = %s AND relative_id = %s',(prisoner_id,relative_id))
            return True
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def delete_prisoner(self,id):
        self.connect()
        try:
            self.cursor.execute('DELETE FROM prisoners WHERE prisoner_id = %s',(id,))
            return True
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def edit_relative(self,data,id):
        self.connect()
        try:
            self.cursor.execute('UPDATE relatives SET title = %s, f_name = %s, l_name = %s, address = %s, tel = %s WHERE relative_id = %s',(*data, id))
            return True
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()
            
    @require_valid_key
    def update_visit_round_and_channel(self,new_round,new_channel,visit_id):
        self.connect()
        try:
            self.cursor.execute('UPDATE visits SET time_visit = %s, channel = %s WHERE visit_id = %s',(new_round,new_channel,visit_id))
            return True
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def remove_visit(self,visit_id):
        self.connect()
        try:
            self.cursor.execute('DELETE FROM visits WHERE visit_id = %s',(visit_id,))
            return True
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def get_visit_by_id(self,visit_id):
        self.connect()
        try:
            self.cursor.execute('SELECT * FROM visits WHERE visit_id = %s',(visit_id,))
            return self.cursor.fetchone()
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

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
                WHERE relations.prisoner_id = %s
            ''',(prisoner_id,))
            return self.cursor.fetchall()
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def count_relative(self,prisoner_id,relative_id):
        self.connect()
        try:
            self.cursor.execute('SELECT count(*) FROM relations WHERE prisoner_id = %s AND relative_id = %s',(prisoner_id,relative_id,))
            return self.cursor.fetchone()[0]
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def prisoner_id_on_table_visits(self,visit_id):
        self.connect()
        try:
            self.cursor.execute('SELECT prisoner_id FROM visits WHERE visit_id = %s',(visit_id,))
            return self.cursor.fetchone()[0]
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def get_execute_manual(self,query):
        self.connect()
        try:
            query = query.replace('?', '%s')
            self.cursor.execute(query)
            return self.cursor.fetchone()[0]
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def set_execute_manual(self,query,params = None):
        self.connect()
        try:
            query = query.replace('?', '%s')
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return True
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def add_relative_to_visits(self,data):
        self.connect()
        print(data)
        try:
            sanitized_data = []
            for item in data:
                if item == '':
                    sanitized_data.append(None)
                else:
                    sanitized_data.append(item)
            self.cursor.execute('UPDATE visits SET relative_id_1 = %s, relative_id_2 = %s, relative_id_3 = %s, relative_id_4 = %s, relative_id_5 = %s WHERE visit_id = %s', sanitized_data)
            return True
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def edit_relation(self,relation,relative_id,prisoner_id):
        self.connect()
        try:
            self.cursor.execute('UPDATE relations SET relation = %s WHERE prisoner_id = %s AND relative_id = %s',(relation,prisoner_id,relative_id))
            return True
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()
            
    @require_valid_key
    def get_relation(self,prisoner_id,relative_id):
        self.connect()
        try:
            self.cursor.execute('SELECT relation FROM relations WHERE prisoner_id = %s AND relative_id = %s',(prisoner_id,relative_id))
            return self.cursor.fetchone()[0]
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def get_channel(self,date,round_time):
        self.connect()
        try:
            self.cursor.execute('SELECT channel FROM visits WHERE date_visit = %s AND time_visit = %s',(date,round_time))
            data = [row[0] for row in self.cursor.fetchall() if row[0] is not None]
            return data
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def update_channel(self,channel,visit_id):
        self.connect()
        try:
            self.cursor.execute('UPDATE visits SET channel = %s WHERE visit_id = %s',(channel,visit_id))
            return True
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    @require_valid_key
    def get_visits_all_on_date(self,date):
        self.connect()
        try:   
            self.cursor.execute('SELECT * FROM visits WHERE date_visit = %s',(date,))
            return self.cursor.fetchall()
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()

    def get_holidays(self):
        self.connect()
        try:
            self.cursor.execute('SELECT date FROM holidays')
            return self.cursor.fetchall()
        except Exception as e:
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
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
            self.conn.rollback()
            func_name = sys._getframe().f_code.co_name
            self.log_error([func_name,str(e)])
            return False
        finally:
            self.close()
        return users

    # ปิดการทำงาน เนื่องจาก Postgres รันแบบ Service มีระบบ Security อยู่แล้ว 
    # ไฟล์ไม่ได้ตั้งค่าเป็น Local DB แบบ SQLite เลยไม่ต้องมี Encode/Decode ให้ถ่วงเครื่อง 
    def decode_db(self):
        pass

    def encode_db(self):
        pass