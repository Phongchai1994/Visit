import sqlite3
import os
from manage.encryption_utils import decrypt_file,encrypt_file
import customtkinter as ctk
from tkinter import messagebox

class SQLiteDB:
    def __init__(self,db_path= 'data/visit_report.db'):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        # โปรแกรมถอดรหัส และเข้ารหัส
        self.EN_DB = 'data/visit_report.db.enc'
        self.DE_DB = 'data/visit_report.db'

    def msgbox(self,e):
        messagebox.showerror('ฐานข้อมูล',f'{e}')

    def connect(self):
        self.conn =sqlite3.connect(self.db_path)
        self.conn.execute('PRAGMA foreign_keys = ON')
        self.cursor = self.conn.cursor()

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
            self.conn.commit()
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

    def get_data_relation(self,id):
        self.decode_db()
        self.connect()

        try:
            self.cursor.execute('SELECT prisoner_id,relative_id FROM relations WHERE prisoner_id = ?',(id,))
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
            self.cursor.execute('SELECT time_stamp,date_visit,time_visit,prisoner_id,relative_id_1,relative_id_2,relative_id_3,relative_id_4,relative_id_5 FROM visits WHERE date_visit = ? AND time_visit = ? ',(data_visit[0],data_visit[1]))
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            self.msgbox(e)
            return False
        finally:
            self.close()
            self.encode_db()

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

    def decode_db(self):
        pass
        # if os.path.exists(self.EN_DB):
        #     decrypt_file(self.EN_DB,self.DE_DB)

    def encode_db(self):
        pass
        # encrypt_file(self.DE_DB,self.EN_DB)

