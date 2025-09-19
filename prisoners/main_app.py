import customtkinter as ctk
import tkinter as tk
from tkinter import ttk,messagebox
from manage.database import SQLiteDB
import emoji
from pyzkfp import ZKFP2
import threading
import time as t
from datetime import datetime,timedelta
from prisoners.card_reader import ThaiIDReader
import os
import tempfile
import time

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape,A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from user_session import user_session, require_admin, require_login

import os
import tempfile
import time

import difflib

pdfmetrics.registerFont(TTFont("TH SarabunPSK", "THSarabun.ttf"))

class RESERVE:
    def __init__(self, main_window, prisoner_data,national_id,to_day,to_month,reserve_now):
        self.status = reserve_now
        self.main_window = main_window
        self.national_id = national_id
        self.follower_vars = []
        self.next_screen = ctk.CTkToplevel(self.main_window)
        
        # สร้างหน้าต่างใหม่
        self.next_screen.configure(fg_color='#f4f7fa')
        # กำหนดขนาดหน้าต่าง
        screen_width = self.next_screen.winfo_screenwidth()
        screen_height = self.next_screen.winfo_screenheight()
        x = (screen_width - 450) // 2
        y = (screen_height - 900) // 2
        self.next_screen.geometry(f'450x900+{x}+{y}')
        # กำหนดชื่อหน้าต่าง
        if self.status:
            self.next_screen.title('เลือกรอบเยี่ยม (จองเยี่ยมปกติ)')
        else:
            self.next_screen.title('เลือกรอบเยี่ยม (จองเยี่ยมล่วงหน้า)')

        self.next_screen.grab_set()
        self.next_screen.attributes('-topmost',True)
        self.next_screen.minsize(450,900)
        self.next_screen.maxsize(450,900)
        self.next_screen.withdraw() # ซ่อนหน้าต่างไว้ก่อน
        # frame เลือกรอบ
        self.frame_select_round = ctk.CTkFrame(self.next_screen, fg_color="#ffffff", corner_radius=16, border_width=2, border_color='#e3eefa')
        # frame เลือกผู้ติดตาม
        self.frame_follower_visit = ctk.CTkFrame(self.next_screen, fg_color='#ffffff', corner_radius=16, border_width=2, border_color='#e3eefa')
        # frame ยืนยันการจอง
        self.frame_confirm_visit = ctk.CTkFrame(self.next_screen, fg_color='#ffffff', corner_radius=16, border_width=2, border_color='#e3eefa')
        # สร้างฐานข้อมูล
        self.db = SQLiteDB()

        self.id = prisoner_data[0]
        self.name = prisoner_data[1]
        self.surname = prisoner_data[2]
        self.level = prisoner_data[3]
        self.dan = prisoner_data[4]
        self.type = prisoner_data[7]

        # กำหนดวันที่ ตั้งค่าวันที่
        self.today = to_day
        self.today_month = to_month

        thai_date = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์","อาทิตย์"]
        dt = datetime.strptime(self.today, "%Y-%m-%d")
        self.thai_day = thai_date[dt.weekday()]

        self.round_visit_var = ctk.StringVar()

        # ชื่อผู้จอง
        self.relative_dict = {}
        data_relatives = self.db.get_relatives_id_fname_lname()
        for rel_id,f_name,l_name in data_relatives:
            full_name = f'{f_name} {l_name}'
            self.relative_dict[rel_id] = full_name


        self.main()

    def main(self):
        if self.check_disciplinary():
            if self.check_visit():
                self.select_round()  # เรียกใช้ฟังก์ชันเลือกเยี่ยม
            else:
                return
        else:
            return

    def on_close(self):
        self.next_screen.destroy()

    def check_disciplinary(self):
        # ตรวจสอบวินัย
        check_disciplinary = self.db.get_data_one(self.id)
        if check_disciplinary[9] == 'ผิดวินัย':
            alert = ALERT(self.main_window,['กรุณาตรวจสอบข้อมูล\nผู้ต้องขังผิดวินัยไม่สามารถจองเยี่ยมได้'],button=False)
            alert.after(3000,lambda: (alert.destroy(),self.next_screen.destroy()))
            return False
        return True

    def check_visit(self):
        # นับครั้งการเยี่ยม return count_today,count_month
        check_visit = self.db.get_count_visit(self.id, self.today, self.today_month)

        if check_visit[0] > 0 :
            alert = ALERT(self.main_window,['กรุณาตรวจสอบข้อมูล\nผู้ต้องขังเยี่ยมได้ไม่เกิน 1 ครั้ง ต่อวัน'],button=False)
            alert.after(3000,lambda: alert.destroy())
            return False
        if self.level == 'เยี่ยม' and check_visit[1] >= 8 :
            alert = ALERT(self.main_window,[f'กรุณาตรวจสอบข้อมูล\nชั้น {self.level}\nเยี่ยมได้ไม่เกิน 8 ครั้ง ต่อเดือน'],button=False)
            alert.after(3000,lambda: alert.destroy())
            return False
        if self.level == 'ดีมาก' and check_visit[1] >= 6 :
            alert = ALERT(self.main_window,[f'กรุณาตรวจสอบข้อมูล\nชั้น {self.level}\nเยี่ยมได้ไม่เกิน 6 ครั้ง ต่อเดือน'],button=False)
            alert.after(3000,lambda: alert.destroy())
            return False
        if self.level == 'ดี' and check_visit[1] >= 4 :
            alert = ALERT(self.main_window,[f'กรุณาตรวจสอบข้อมูล\nชั้น {self.level}\nเยี่ยมได้ไม่เกิน 4 ครั้ง ต่อเดือน'],button=False)
            alert.after(3000,lambda: alert.destroy())
            return False
        if self.level == 'กลาง' and check_visit[1] >= 3 :
            alert = ALERT(self.main_window,[f'กรุณาตรวจสอบข้อมูล\nชั้น {self.level}\nเยี่ยมได้ไม่เกิน 3 ครั้ง ต่อเดือน'],button=False)
            alert.after(3000,lambda: alert.destroy())
            return False
        if self.level == 'ระหว่างพิจารณาคดี' and check_visit[1] >= 3 :
            alert = ALERT(self.main_window,[f'กรุณาตรวจสอบข้อมูล\nชั้น {self.level}\nเยี่ยมได้ไม่เกิน 3 ครั้ง ต่อเดือน'],button=False)
            alert.after(3000,lambda: alert.destroy())
            return False
        if self.level == 'ปรับปรุง' and check_visit[1] >= 2 :
            alert = ALERT(self.main_window,[f'กรุณาตรวจสอบข้อมูล\nชั้น {self.level}\nเยี่ยมได้ไม่เกิน 2 ครั้ง ต่อเดือน'],button=False)
            alert.after(3000,lambda: alert.destroy())
            return False
        if self.level == 'ปรับปรุงมาก' and check_visit[1] >= 1 :
            alert = ALERT(self.main_window,[f'กรุณาตรวจสอบข้อมูล\nชั้น {self.level}\nเยี่ยมได้ไม่เกิน 1 ครั้ง ต่อเดือน'],button=False)
            alert.after(3000,lambda: alert.destroy())
            return False
        return True
    
    # เลือกรอบเยี่ยม
    def select_round(self):
        # แสดงหน้าต่างเมื่อจะใช้งานจริง
        self.next_screen.deiconify() 

        morning = MORING_ROUNDS()
        afternoon = AFTERNOON_ROUNDS()
        for widget in self.frame_select_round.winfo_children():
            widget.destroy()

        self.frame_follower_visit.pack_forget()
        self.frame_select_round.pack(fill='both', expand=True)
        thai_date = self.get_thai_date(self.today)
        if self.status:
            label = ctk.CTkLabel(self.frame_select_round, text=f'เลือกรอบเยี่ยม (จองเยี่ยมวันนี้)\n{thai_date}', font=('TH SarabunPSK', 40, 'bold'),text_color="#FF0505")
        else:
            label = ctk.CTkLabel(self.frame_select_round, text=f'เลือกรอบเยี่ยม (ล่วงหน้า)\n{thai_date}', font=('TH SarabunPSK', 40, 'bold'),text_color="#FF0505")

        label.pack(pady=5)
        content = ctk.CTkLabel(self.frame_select_round, text=f'{self.name} {self.surname}', font=('TH SarabunPSK', 35))
        content.pack(pady=5)
        now = datetime.now().time()
        if self.status:
            if self.dan == 'รจช':
                # 🔹 รอบเช้า (เวลาแสดง, เวลาเริ่มจริง, เวลาปิด)
                rounds = [
                    ('เวลา 12.00 - 13.00', '12:00:00', '12:50:00')
                ]
                for text, start, close in rounds:
                    close_time = datetime.strptime(close, "%H:%M:%S").time()
                    if now < close_time:
                        ctk.CTkRadioButton(
                            self.frame_select_round,
                            text=text,
                            variable=self.round_visit_var,
                            value=start,
                            font=('TH SarabunPSK', 35, 'bold')
                        ).pack(pady=5)
            elif self.thai_day == 'จันทร์' and str(self.dan) == '6':
                # 🔹 รอบเช้า (เวลาแสดง, เวลาเริ่มจริง, เวลาปิด)
                ctk.CTkLabel(self.frame_select_round, text='รอบเช้า', font=('TH SarabunPSK', 35, 'bold')).pack(pady=10)
                for text, start in morning.get_available_rounds(now):
                    ctk.CTkRadioButton(
                        self.frame_select_round,
                        text=text,
                        variable=self.round_visit_var,
                        value=start,
                        font=('TH SarabunPSK', 35, 'bold')
                    ).pack(pady=5)

                # 🔹 รอบบ่าย
                ctk.CTkLabel(self.frame_select_round, text='รอบบ่าย', font=('TH SarabunPSK', 35, 'bold')).pack(pady=10)
                for text, start in afternoon.get_available_rounds(now):
                    ctk.CTkRadioButton(
                        self.frame_select_round,
                        text=text,
                        variable=self.round_visit_var,
                        value=start,
                        font=('TH SarabunPSK', 35, 'bold')
                    ).pack(pady=5)                                                                                                          
            elif self.thai_day == 'อังคาร' and str(self.dan) == '5':
                # 🔹 รอบเช้า (เวลาแสดง, เวลาเริ่มจริง, เวลาปิด)
                ctk.CTkLabel(self.frame_select_round, text='รอบเช้า', font=('TH SarabunPSK', 35, 'bold')).pack(pady=10)
                for text, start in morning.get_available_rounds(now):
                    ctk.CTkRadioButton(
                        self.frame_select_round,
                        text=text,
                        variable=self.round_visit_var,
                        value=start,
                        font=('TH SarabunPSK', 35, 'bold')
                    ).pack(pady=5)
                
                # 🔹 รอบบ่าย
                ctk.CTkLabel(self.frame_select_round, text='รอบบ่าย', font=('TH SarabunPSK', 35, 'bold')).pack(pady=10)
                for text, start in afternoon.get_available_rounds(now):
                    ctk.CTkRadioButton(
                        self.frame_select_round,
                        text=text,
                        variable=self.round_visit_var,
                        value=start,
                        font=('TH SarabunPSK', 35, 'bold')
                    ).pack(pady=5) 
            elif self.thai_day == 'พุธ' and str(self.dan) == '1' and self.type != 'ผู้ต้องกักขัง':
                # 🔹 รอบเช้า (เวลาแสดง, เวลาเริ่มจริง, เวลาปิด)
                ctk.CTkLabel(self.frame_select_round, text='รอบเช้า', font=('TH SarabunPSK', 35, 'bold')).pack(pady=10)
                for text, start in morning.get_available_rounds(now):
                    ctk.CTkRadioButton(
                        self.frame_select_round,
                        text=text,
                        variable=self.round_visit_var,
                        value=start,
                        font=('TH SarabunPSK', 35, 'bold')
                    ).pack(pady=5)
            elif self.thai_day == 'พุธ' and str(self.dan) == '1' and self.type == 'ผู้ต้องกักขัง':
                # 🔹 ให้เฉพาะรอบ 4
                rounds = [
                    ('เวลา 11.00 - 11.15', '11:00:00', '10:45:00')
                ]
                for text, start, close in rounds:
                    close_time = datetime.strptime(close, "%H:%M:%S").time()
                    if now < close_time:
                        ctk.CTkRadioButton(
                            self.frame_select_round,
                            text=text,
                            variable=self.round_visit_var,
                            value=start,
                            font=('TH SarabunPSK', 35, 'bold')
                        ).pack(pady=5)
            elif self.thai_day == 'พุธ' and str(self.dan) in ['2','3','4','7'] and self.type != 'ผู้ต้องกักขัง':                    
                # 🔹 รอบบ่าย
                ctk.CTkLabel(self.frame_select_round, text='รอบบ่าย', font=('TH SarabunPSK', 35, 'bold')).pack(pady=10)
                for text, start in afternoon.get_available_rounds(now):
                    ctk.CTkRadioButton(
                        self.frame_select_round,
                        text=text,
                        variable=self.round_visit_var,
                        value=start,
                        font=('TH SarabunPSK', 35, 'bold')
                    ).pack(pady=5) 
            elif self.thai_day == 'พุธ' and str(self.dan) in ['4','7'] and self.type == 'ผู้ต้องกักขัง':
                #  🔹 รอบบ่าย ให้เฉพาะรอบ 7
                rounds = [
                    ('เวลา 14.15 - 14.30', '14:15:00', '13:15:00')
                ]
                for text, start, close in rounds:
                    close_time = datetime.strptime(close, "%H:%M:%S").time()
                    if now < close_time:
                        ctk.CTkRadioButton(
                            self.frame_select_round,
                            text=text,
                            variable=self.round_visit_var,
                            value=start,
                            font=('TH SarabunPSK', 35, 'bold')
                        ).pack(pady=5)
            elif self.thai_day == 'พฤหัสบดี' and str(self.dan) == '5':
                # 🔹 รอบเช้า (เวลาแสดง, เวลาเริ่มจริง, เวลาปิด)
                ctk.CTkLabel(self.frame_select_round, text='รอบเช้า', font=('TH SarabunPSK', 35, 'bold')).pack(pady=10)
                for text, start in morning.get_available_rounds(now):
                    ctk.CTkRadioButton(
                        self.frame_select_round,
                        text=text,
                        variable=self.round_visit_var,
                        value=start,
                        font=('TH SarabunPSK', 35, 'bold')
                    ).pack(pady=5)               
            elif self.thai_day == 'พฤหัสบดี' and str(self.dan) == '6':
                # 🔹 รอบบ่าย
                ctk.CTkLabel(self.frame_select_round, text='รอบบ่าย', font=('TH SarabunPSK', 35, 'bold')).pack(pady=10)
                for text, start in afternoon.get_available_rounds(now):
                    ctk.CTkRadioButton(
                        self.frame_select_round,
                        text=text,
                        variable=self.round_visit_var,
                        value=start,
                        font=('TH SarabunPSK', 35, 'bold')
                    ).pack(pady=5)
            elif self.thai_day == 'ศุกร์' and str(self.dan) == '1' and self.type != 'ผู้ต้องกักขัง':
                # 🔹 รอบเช้า (เวลาแสดง, เวลาเริ่มจริง, เวลาปิด)
                ctk.CTkLabel(self.frame_select_round, text='รอบเช้า', font=('TH SarabunPSK', 35, 'bold')).pack(pady=10)
                for text, start in morning.get_available_rounds(now):
                    ctk.CTkRadioButton(
                        self.frame_select_round,
                        text=text,
                        variable=self.round_visit_var,
                        value=start,
                        font=('TH SarabunPSK', 35, 'bold')
                    ).pack(pady=5)
            elif self.thai_day == 'ศุกร์' and str(self.dan) == '1' and self.type == 'ผู้ต้องกักขัง':
                # 🔹 ให้เฉพาะรอบ 4
                rounds = [
                    ('เวลา 11.00 - 11.15', '11:00:00', '10:45:00')
                ]
                for text, start, close in rounds:
                    close_time = datetime.strptime(close, "%H:%M:%S").time()
                    if now < close_time:
                        ctk.CTkRadioButton(
                            self.frame_select_round,
                            text=text,
                            variable=self.round_visit_var,
                            value=start,
                            font=('TH SarabunPSK', 35, 'bold')
                        ).pack(pady=5)
            elif self.thai_day == 'ศุกร์' and str(self.dan) in ['2','3','4','7'] and self.type != 'ผู้ต้องกักขัง':                    
                # 🔹 รอบบ่าย
                ctk.CTkLabel(self.frame_select_round, text='รอบบ่าย', font=('TH SarabunPSK', 35, 'bold')).pack(pady=10)
                for text, start in afternoon.get_available_rounds(now):
                    ctk.CTkRadioButton(
                        self.frame_select_round,
                        text=text,
                        variable=self.round_visit_var,
                        value=start,
                        font=('TH SarabunPSK', 35, 'bold')
                    ).pack(pady=5)
            elif self.thai_day == 'ศุกร์' and str(self.dan) in ['4','7'] and self.type == 'ผู้ต้องกักขัง':
                #  🔹 รอบบ่าย ให้เฉพาะรอบ 7
                rounds = [
                    ('เวลา 14.15 - 14.30', '14:15:00', '13:15:00')
                ]
                for text, start, close in rounds:
                    close_time = datetime.strptime(close, "%H:%M:%S").time()
                    if now < close_time:
                        ctk.CTkRadioButton(
                            self.frame_select_round,
                            text=text,
                            variable=self.round_visit_var,
                            value=start,
                            font=('TH SarabunPSK', 35, 'bold')
                        ).pack(pady=5)
        else:
            morning_rounds = [
                ('รอบที่ 1 เวลา 09.30 - 09.45', '09:30:00'),
                ('รอบที่ 2 เวลา 10.00 - 10.15', '10:00:00'),
                ('รอบที่ 3 เวลา 10.30 - 10.45', '10:30:00'),
                ('รอบที่ 4 เวลา 11.00 - 11.15', '11:00:00'),
                ]

            afternoon_rounds = [
                ('รอบที่ 5 เวลา 13.15 - 13.30', '13:15:00'),
                ('รอบที่ 6 เวลา 13.45 - 14.00', '13:45:00'),
                ('รอบที่ 7 เวลา 14.15 - 14.30', '14:15:00'),
                ]

            if self.dan == 'รจช':
                # 🔹 รอบเช้า (เวลาแสดง, เวลาเริ่มจริง)
                rounds = [
                    ('เวลา 12.00 - 13.00', '12:00:00')
                ]
                for text, start in rounds:
                    ctk.CTkRadioButton(
                        self.frame_select_round,
                        text=text,
                        variable=self.round_visit_var,
                        value=start,
                        font=('TH SarabunPSK', 35, 'bold')
                    ).pack(pady=5)

            elif self.thai_day == 'จันทร์' and str(self.dan) == '6':
                # 🔹 รอบเช้า (เวลาแสดง, เวลาเริ่มจริง, เวลาปิด)
                ctk.CTkLabel(self.frame_select_round, text='รอบเช้า', font=('TH SarabunPSK', 35, 'bold')).pack(pady=10)
                for text, start in morning_rounds:
                    ctk.CTkRadioButton(
                        self.frame_select_round,
                        text=text,
                        variable=self.round_visit_var,
                        value=start,
                        font=('TH SarabunPSK', 35, 'bold')
                    ).pack(pady=5)

                # 🔹 รอบบ่าย
                ctk.CTkLabel(self.frame_select_round, text='รอบบ่าย', font=('TH SarabunPSK', 35, 'bold')).pack(pady=10)
                for text, start in afternoon_rounds:
                    ctk.CTkRadioButton(
                        self.frame_select_round,
                        text=text,
                        variable=self.round_visit_var,
                        value=start,
                        font=('TH SarabunPSK', 35, 'bold')
                    ).pack(pady=5)
            elif self.thai_day == 'อังคาร' and str(self.dan) == '5':
                # 🔹 รอบเช้า (เวลาแสดง, เวลาเริ่มจริง, เวลาปิด)
                ctk.CTkLabel(self.frame_select_round, text='รอบเช้า', font=('TH SarabunPSK', 35, 'bold')).pack(pady=10)
                for text, start in morning_rounds:
                    ctk.CTkRadioButton(
                        self.frame_select_round,
                        text=text,
                        variable=self.round_visit_var,
                        value=start,
                        font=('TH SarabunPSK', 35, 'bold')
                    ).pack(pady=5)

                # 🔹 รอบบ่าย
                ctk.CTkLabel(self.frame_select_round, text='รอบบ่าย', font=('TH SarabunPSK', 35, 'bold')).pack(pady=10)
                for text, start in afternoon_rounds:
                    ctk.CTkRadioButton(
                        self.frame_select_round,
                        text=text,
                        variable=self.round_visit_var,
                        value=start,
                        font=('TH SarabunPSK', 35, 'bold')
                    ).pack(pady=5)
            elif self.thai_day == 'พุธ' and str(self.dan) == '1':
                # 🔹 รอบเช้า (เวลาแสดง, เวลาเริ่มจริง, เวลาปิด)
                ctk.CTkLabel(self.frame_select_round, text='รอบเช้า', font=('TH SarabunPSK', 35, 'bold')).pack(pady=10)
                for text, start in morning_rounds:
                    ctk.CTkRadioButton(
                        self.frame_select_round,
                        text=text,
                        variable=self.round_visit_var,
                        value=start,
                        font=('TH SarabunPSK', 35, 'bold')
                    ).pack(pady=5)
            elif self.thai_day == 'พุธ' and str(self.dan) in ['2','3','4','7']:
                # 🔹 รอบบ่าย
                ctk.CTkLabel(self.frame_select_round, text='รอบบ่าย', font=('TH SarabunPSK', 35, 'bold')).pack(pady=10)
                for text, start in afternoon_rounds:
                    ctk.CTkRadioButton(
                        self.frame_select_round,
                        text=text,
                        variable=self.round_visit_var,
                        value=start,
                        font=('TH SarabunPSK', 35, 'bold')
                    ).pack(pady=5)
            elif self.thai_day == 'พฤหัสบดี' and str(self.dan) == '5':
                # 🔹 รอบเช้า (เวลาแสดง, เวลาเริ่มจริง, เวลาปิด)
                ctk.CTkLabel(self.frame_select_round, text='รอบเช้า', font=('TH SarabunPSK', 35, 'bold')).pack(pady=10)
                for text, start in morning_rounds:
                    ctk.CTkRadioButton(
                        self.frame_select_round,
                        text=text,
                        variable=self.round_visit_var,
                        value=start,
                        font=('TH SarabunPSK', 35, 'bold')
                    ).pack(pady=5)
            elif self.thai_day == 'พฤหัสบดี' and str(self.dan) == '6':
                # 🔹 รอบบ่าย
                ctk.CTkLabel(self.frame_select_round, text='รอบบ่าย', font=('TH SarabunPSK', 35, 'bold')).pack(pady=10)
                for text, start in afternoon_rounds:
                    ctk.CTkRadioButton(
                        self.frame_select_round,
                        text=text,
                        variable=self.round_visit_var,
                        value=start,
                        font=('TH SarabunPSK', 35, 'bold')
                    ).pack(pady=5)
            elif str(self.dan) == '1':

                # 🔹 รอบเช้า (เวลาแสดง, เวลาเริ่มจริง, เวลาปิด)
                ctk.CTkLabel(self.frame_select_round, text='รอบเช้า', font=('TH SarabunPSK', 35, 'bold')).pack(pady=10)
                for text, start in morning_rounds:
                    ctk.CTkRadioButton(
                        self.frame_select_round,
                        text=text,
                        variable=self.round_visit_var,
                        value=start,
                        font=('TH SarabunPSK', 35, 'bold')
                    ).pack(pady=5)
            elif str(self.dan) in ['2','3','4','7']:
                # 🔹 รอบบ่าย
                ctk.CTkLabel(self.frame_select_round, text='รอบบ่าย', font=('TH SarabunPSK', 35, 'bold')).pack(pady=10)
                for text, start in afternoon_rounds:
                    ctk.CTkRadioButton(
                        self.frame_select_round,
                        text=text,
                        variable=self.round_visit_var,
                        value=start,
                        font=('TH SarabunPSK', 35, 'bold')
                    ).pack(pady=5)
        # 🔸 ปุ่ม
        submit = ctk.CTkButton(
            self.frame_select_round,
            text='เลือกผู้ติดตาม',
            command=lambda: self.select_follower() if self.round_visit_var.get() else ALERT(self.frame_select_round, msg=['\nกรุณาเลือกรอบเยี่ยม']),
            font=('TH SarabunPSK', 32, 'bold'),
            height=100
        )

        cancel = ctk.CTkButton(
            self.frame_select_round,
            text='ยกเลิก',
            command=lambda:(self.on_close()),
            font=('TH SarabunPSK', 32, 'bold'),
            height=40,
            fg_color='red'
        )

        cancel.pack(side='bottom', pady=10)
        submit.pack(side='bottom', pady=10)

    def select_follower(self):
        for widget in self.frame_follower_visit.winfo_children():
            widget.destroy()
        self.frame_select_round.pack_forget()
        self.frame_confirm_visit.pack_forget()
        date_current = datetime.now().strftime("%Y-%m-%d")


        # date time จากการเลือกรอบเยี่ยม
        round_time = self.round_visit_var.get()
        round_time_strtime = (datetime.strptime(round_time,"%H:%M:%S")).strftime("%H:%M:%S")
        count_visit = self.db.get_count_visit_on_round(round_time,self.today)
        channel_on_db = self.db.get_channel(self.today,round_time_strtime)
        print(f'channel_on_db = {channel_on_db} and type = {type(channel_on_db)}')
        sorted_channel_on_db = sorted(channel_on_db)
        channel = 1

        for index,value in enumerate(sorted_channel_on_db):
            print(index,value)
            if index+1 != int(value):
                channel = index + 1
                print(f'channel ช่องว่าง = {channel}')
                break
            elif index == len(sorted_channel_on_db) - 1:
                channel = index + 2
                print(f'channel ตัวสุดท้าย = {channel}')
        print(f'ค่าที่เติม = {channel}')
        
        if count_visit > 14:
            count_alert = ALERT(self.next_screen,['รอบเต็ม\nกรุณาเลือกรอบใหม่'],text_color='red',button=True)
            self.select_round()
            return

        self.frame_follower_visit.pack(fill = 'both',expand = True)
        text_from_round = f'จองเยี่ยม\n{self.name} {self.surname}\nเยี่ยมเวลา {self.round_visit_var.get()} น.'
        ctk.CTkLabel(self.frame_follower_visit,text=text_from_round,font=('TH SarabunPSK',35)).pack(pady = 10)

        followers = self.db.get_join_prisoners_and_relatives_not_follower(self.id,self.national_id)

        ctk.CTkLabel(self.frame_follower_visit,text='กรุณาเลือกผู้ติดตาม',font=('TH SarabunPSK',38,'bold')).pack(pady = 10)
        ctk.CTkLabel(self.frame_follower_visit,text='(เลือกผู้ติดตามได้สูงสุด 4 คน)',text_color='red',font=('TH SarabunPSK',28,'bold')).pack(pady = 10)
        if followers:
            for follower in followers:
                rid,title,fname,lname = follower
                if str(rid) == self.national_id:
                    break
                var = ctk.BooleanVar()
                chk = ctk.CTkCheckBox(self.frame_follower_visit,
                                    text=f'{title}{fname} {lname}',
                                    variable=var,
                                    font=('TH SarabunPSK',35,'bold'))
                chk.pack(pady = 5,padx = 50,anchor = 'nw')
                self.follower_vars.append((rid,var))
        else:
            ctk.CTkLabel(self.frame_follower_visit,text='ไม่มีผู้ติดตาม',font=('TH SarabunPSK',32,'bold')).pack(pady = 10)

        submit = ctk.CTkButton(self.frame_follower_visit,
                            text='ถัดไป',
                            command=lambda:self.confirm_visit(round_time_strtime,self.today,channel),
                            font=('TH SarabunPSK',32,'bold'),
                            height=100
                            )

        cancel = ctk.CTkButton(self.frame_follower_visit,
                            text='ย้อนกลับ',
                            command=lambda:self.select_round(),
                            font=('TH SarabunPSK',32,'bold'),
                            height=40,
                            fg_color='orange'
                            )
        cancel.pack(side = 'bottom',pady = 10)
        submit.pack(side = 'bottom',pady = 10)
    
    # ยืนยันข้อมูล
    def confirm_visit(self,round_time_strtime,reserve_date,channel):
        channel = channel
        for widget in self.frame_confirm_visit.winfo_children():
            widget.destroy()

        self.frame_follower_visit.pack_forget()
        self.frame_confirm_visit.pack(fill = 'both',expand = True)
        ctk.CTkLabel(self.frame_confirm_visit,text='กรุณาตรวจสอบข้อมูลให้ถูกต้อง',font=('TH SarabunPSK',30,'bold')).pack(pady = 20)
        select_fl_id = [rid for rid,var in self.follower_vars if var.get()]
        prepare_data = [reserve_date,round_time_strtime,self.id,self.national_id]

        thai_date = self.get_thai_date(self.today)

        ctk.CTkLabel(self.frame_confirm_visit,text=f'จองเยี่ยม\n{self.name} {self.surname}\n{thai_date}\nเวลา {self.round_visit_var.get()} น.\nช่องเยี่ยมที่ {channel}\nโดย {self.relative_dict.get(int(self.national_id))}\nผู้ติดตาม',font=('TH SarabunPSK',35)).pack(pady = 5)
        for index,row in enumerate(select_fl_id):
            prepare_data.append(row)
            ctk.CTkLabel(self.frame_confirm_visit,text=f'คนที่ {index +1} {self.relative_dict.get(row)}',font=('TH SarabunPSK',35)).pack(pady = 5)

        select_fl_id.clear()

        if len(prepare_data) > 8:
            print(f'ใน if = {prepare_data}')
            prepare_data.clear()
            self.follower_vars.clear()
            self.select_follower()
            alert = ALERT(self.frame_follower_visit,msg=['เลือกผู้ติดตามได้ไม่เกิน 4 คน','กรุณาเลือกใหม่'])
        
        def on_confirm():
            # ซ่อนปุ่มเพื่อป้องกันการกดซ้ำ แล้วค่อยบันทึกข้อมูล
            submit.grid_forget()
            self.insert_reserve_visit_to_db(prepare_data,channel)

        submit = ctk.CTkButton(self.frame_confirm_visit,
                            text='ยืนยันการจองเยี่ยม',
                            command=on_confirm,
                            font=('TH SarabunPSK',32,'bold'),
                            height=100
                            )

        back = ctk.CTkButton(self.frame_confirm_visit,
                            text='ย้อนกลับ',
                            command=lambda:go_back(),
                            font=('TH SarabunPSK',32,'bold'),
                            height=40,
                            fg_color='orange'
                            )
        cancel = ctk.CTkButton(self.frame_confirm_visit,
                            text='ยกเลิกการจอง',
                            command=lambda:(self.on_close()),
                            font=('TH SarabunPSK',32,'bold'),
                            height=40,
                            fg_color='red'
                            )
        cancel.pack(side = 'bottom',pady = 20)
        back.pack(side = 'bottom',pady = 20)
        submit.pack(side = 'bottom',pady = 20)

        def go_back():
            prepare_data.clear()
            self.follower_vars.clear()
            self.select_follower()
        return True

    def insert_reserve_visit_to_db(self,prepare_data,channel):
        if len(prepare_data) == 8:
            query = "INSERT INTO visits (date_visit,time_visit,prisoner_id,relative_id_1,relative_id_2,relative_id_3,relative_id_4,relative_id_5) VALUES (?,?,?,?,?,?,?,?)"
            result = self.db.add_visits(query,prepare_data)
            if result:
                result = self.db.add_channel_on_visits(prepare_data[:4],channel)
                if result:
                    self.insert_succress()
                    return
        elif len(prepare_data) == 7:
            query = "INSERT INTO visits (date_visit,time_visit,prisoner_id,relative_id_1,relative_id_2,relative_id_3,relative_id_4) VALUES (?,?,?,?,?,?,?)"
            result = self.db.add_visits(query,prepare_data)
            if result:
                result = self.db.add_channel_on_visits(prepare_data[:4],channel)
                if result:
                    self.insert_succress()
                    return
        elif len(prepare_data) == 6:
            query = "INSERT INTO visits (date_visit,time_visit,prisoner_id,relative_id_1,relative_id_2,relative_id_3) VALUES (?,?,?,?,?,?)"
            result = self.db.add_visits(query,prepare_data)
            if result:
                result = self.db.add_channel_on_visits(prepare_data[:4],channel)
                if result:
                    self.insert_succress()
                    return
        elif len(prepare_data) == 5:
            query = "INSERT INTO visits (date_visit,time_visit,prisoner_id,relative_id_1,relative_id_2) VALUES (?,?,?,?,?)"
            result = self.db.add_visits(query,prepare_data)
            if result:
                result = self.db.add_channel_on_visits(prepare_data[:4],channel)
                if result:
                    self.insert_succress()
                    return
        elif len(prepare_data) == 4:
            query = "INSERT INTO visits (date_visit,time_visit,prisoner_id,relative_id_1) VALUES (?,?,?,?)"
            result = self.db.add_visits(query,prepare_data)
            if result:
                result = self.db.add_channel_on_visits(prepare_data[:4],channel)
                if result:
                    self.insert_succress()
                    return
        return True
    
    def insert_succress(self):
        alert = ALERT(self.next_screen,['จองเยี่ยมสำเร็จ'],button=True)
        result =alert.show()
        if result:
            self.on_close()
        return True
    
    def get_thai_date(self,date_str):
        thai_days = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
        thai_months = [
            "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
            "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
        ]
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        weekday = thai_days[dt.weekday()]
        month = thai_months[dt.month - 1]
        year_th = dt.year + 543
        return f"วัน{weekday} ที่ {dt.day} {month} {year_th}"

class CALCULATE_NEXT_DAY:
    def __init__(self):
        self.db = SQLiteDB()
        self.date_db = self.db.get_holidays()
        self.today_str = datetime.today().strftime("%Y-%m-%d")
        self.today_obj = datetime.strptime(self.today_str, "%Y-%m-%d")
        self.next_day_obj = self.today_obj + timedelta(days=1)

    def get_next_day(self):

        while any(value[0] == self.next_day_obj.strftime("%Y-%m-%d") for value in self.date_db):
            self.next_day_obj += timedelta(days=1)

        return self.next_day_obj.strftime("%Y-%m-%d")
    
    def get_weekday_thai(self):
        thai_days = ['จันทร์', 'อังคาร', 'พุธ', 'พฤหัสบดี', 'ศุกร์', 'เสาร์', 'อาทิตย์']
        return thai_days[self.next_day_obj.weekday()]

class MORING_ROUNDS:
    """คลาสสำหรับจัดการข้อมูลรอบเช้า"""
    def __init__(self):
        self.rounds = [
            ('รอบที่ 1 เวลา 09.30 - 09.45', '09:30:00', '09:15:00'),
            ('รอบที่ 2 เวลา 10.00 - 10.15', '10:00:00', '09:45:00'),
            ('รอบที่ 3 เวลา 10.30 - 10.45', '10:30:00', '10:15:00'),
            ('รอบที่ 4 เวลา 11.00 - 11.15', '11:00:00', '10:15:00'),
        ]

    def get_available_rounds(self, now):
        """คืนค่ารอบที่ยังสามารถเลือกได้ตามเวลาปัจจุบัน"""
        from datetime import datetime
        available = []
        for text, start, close in self.rounds:
            close_time = datetime.strptime(close, "%H:%M:%S").time()
            if now < close_time:
                available.append((text, start))
        return available   

class AFTERNOON_ROUNDS:
    """คลาสสำหรับจัดการข้อมูลรอบบ่าย"""
    def __init__(self):
        self.rounds = [
            ('รอบที่ 5 เวลา 13.15 - 13.30', '13:15:00', '13:00:00'),
            ('รอบที่ 6 เวลา 13.45 - 14.00', '13:45:00', '13:15:00'),
            ('รอบที่ 7 เวลา 14.15 - 14.30', '14:15:00', '13:15:00'),
        ]

    def get_available_rounds(self, now):
        """คืนค่ารอบที่ยังสามารถเลือกได้ตามเวลาปัจจุบัน"""
        from datetime import datetime
        available = []
        for text, start, close in self.rounds:
            close_time = datetime.strptime(close, "%H:%M:%S").time()
            if now < close_time:
                available.append((text, start))
        return available
    
class ALERT(ctk.CTkToplevel):
    def __init__(self, parent, msg=None, text_color=None, button=True):
        super().__init__(parent)
        self.result = False  # เพิ่มตัวแปรสถานะ
        self.geometry('300x200+840+440')
        self.grab_set()
        self.focus()
        self.attributes('-topmost', True)
        self.title('แจ้งเตือน')
        self.overrideredirect(True)
        self.configure(fg_color='#f4f7fa')  # เพิ่มสีพื้นหลังให้สอดคล้องกับธีม
        frame_border = ctk.CTkFrame(self, corner_radius=5, fg_color='#2d3a4b')  # เปลี่ยนจาก black เป็นสีธีม
        frame_border.pack(fill='both', expand=True, padx=2, pady=2)
        frame_inner = ctk.CTkFrame(frame_border, corner_radius=3, fg_color='#ffffff')  # เพิ่มสีพื้นหลังสีขาว
        frame_inner.pack(fill='both', expand=True, padx=3, pady=3)
        if text_color is None:
            text_color = 'red'
        if msg is None:
            msg = ['เกิดข้อผิดพลาด']
        for line in msg:
            ctk.CTkLabel(
                frame_inner,
                text=line,
                text_color=text_color,
                font=('TH SarabunPSK', 28, 'bold')
            ).pack(pady=10)
        if button:
            ctk.CTkButton(
                frame_inner,
                text='รับทราบ',
                font=('TH SarabunPSK', 28, 'bold'),
                command=self._on_ok
            ).pack(side='bottom', pady=20)
        self.protocol("WM_DELETE_WINDOW", self._on_ok)
        self.bind('<Return>',lambda e: self._on_ok())

    def _on_ok(self):
        self.result = True
        self.destroy()

    def show(self):
        self.wait_window()
        return self.result
            
class MainFrame(ctk.CTkFrame):
    def __init__(self,parent):
        super().__init__(parent,fg_color='#f4f7fa')  # เปลี่ยนจาก bg_color='#D7F197' เป็น fg_color='#f4f7fa'

        self.grid(row=0,column=1,sticky='nsew')
        self.db = SQLiteDB()
        
        # ✅ ตรวจสอบและแสดง path ฐานข้อมูลเมื่อเริ่มต้น
        print(f"Database path: {self.db.db_path}")
        if self.db.db_path and os.path.exists(self.db.db_path):
            print("✅ ไฟล์ฐานข้อมูลพบแล้ว")
        else:
            print(f"❌ ไม่พบไฟล์ฐานข้อมูล: {self.db.db_path}")
        
        self.zkfp2 = ZKFP2()
        self.thai_id_reader = ThaiIDReader()

        # สร้าง Frame ลงทะเบียนผู้ต้องขัง #
        self.register_frame = ctk.CTkFrame(self, fg_color='#f8fbff', corner_radius=20, border_width=2, border_color='#e3eefa')

        # สร้าง Frame เมนูค้นหาผู้ต้องขังเพือจัดการญาติ #
        self.showdata_frame = ctk.CTkFrame(self, fg_color='#f0f8f0', corner_radius=20, border_width=2, border_color='#d4e6d4')

        # สร้าง Frame เมนู ย้ายแดน และปรับชั้น #
        self.move_dan_and_adjust_level_frame = ctk.CTkFrame(self, fg_color='#fff8f0', corner_radius=20, border_width=2, border_color='#f4e6d4')

        # สร้าง Frame แสดงข้อมูลผู้ต้องขังทั้งหมดเป็นตาราง #
        self.show_all_prisoner_frame = ctk.CTkFrame(self, fg_color='#f8f0ff', corner_radius=20, border_width=2, border_color='#e6d4f4')

        # สร้าง Frame แสดงข้อมูลญาติทั้งหมดเป็นตาราง 
        self.show_all_relative_frame = ctk.CTkFrame(self, fg_color='#f0fff0', corner_radius=20, border_width=2, border_color='#d4f4d4')

        # สร้าง Frame สำหรับรายงานประวัติการเยี่ยมญาติ
        self.popup_report_visits = ctk.CTkFrame(self, fg_color='#fff0f8', corner_radius=20, border_width=2, border_color='#f4d4e6')

        # สร้าง Frame สำหรับรายงานประจำเดือน
        self.popup_report_visit_on_month = ctk.CTkFrame(self, fg_color='#f0f8ff', corner_radius=20, border_width=2, border_color='#d4e6f4')

        # สร้าง Frame สำหรับจองเยี่ยมญาติด้วยหมายเลขบัตรประชาชน
        self.reserve_visit_by_national_id_frame = ctk.CTkFrame(self, fg_color='#f0f8ff', corner_radius=20, border_width=2, border_color='#d4e6f4')

        # สร้าง Frame สำหรับจองเยี่ยมญาติ
        self.reserve_visit_frame = ctk.CTkFrame(self, fg_color='#f0f8ff', corner_radius=20, border_width=2, border_color='#d4e6f4')

        # สร้าง Frame สำหรับลงทะเบียนลายนิ้วมือ
        self.fingerprint_frame = ctk.CTkFrame(self, fg_color='#fff8f0', corner_radius=20, border_width=2, border_color='#f4e6d4')

        # ใช้ตรวจสอบการป้อนตัวเลขใน regis_entry_id
        self.vcmd = self.register(self.validate_number_input)

        self.open_nextscreen_window = None
##############################################################################################################################################################################
#   เช็คการกรอกข้อมูล ให้กรอกเฉพาะตัวเลข
##############################################################################################################################################################################
    def validate_number_input(self,new_value):
        return new_value.isdigit() or new_value ==''  

##############################################################################################################################################################################
#   ลงทะเบียนผู้ต้องขัง 
##############################################################################################################################################################################
    def register_prisoner(self):
        # Modern card style with matching theme colors
        self.register_frame.configure(fg_color="#f8fbff", corner_radius=24, border_width=2, border_color='#e3eefa')
        self.register_frame.grid_columnconfigure((0, 1), weight=1, uniform="register_frame")
        self.register_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9), weight=1, uniform="register_frame")
        for i in range(10):
            self.register_frame.grid_rowconfigure(i, minsize=48)

        # Header with enhanced styling
        regis_label_content = ctk.CTkLabel(
            self.register_frame,
            text='ลงทะเบียนผู้ต้องขัง',
            font=('TH SarabunPSK', 44, 'bold'),
            text_color='#2d3a4b'
        )
        regis_label_content.grid(row=0, column=0, columnspan=2, sticky='nsew', pady=(24, 10))

        # ID
        regis_label_id = ctk.CTkLabel(self.register_frame, text='รหัสประจำตัว : ',
            font=('TH SarabunPSK', 20, 'bold'), text_color='#4a4a4a')
        regis_label_id.grid(row=1, column=0, sticky='e', padx=12)
        regis_entry_id = ctk.CTkEntry(self.register_frame, font=('TH SarabunPSK', 20),
            width=220, border_width=2, corner_radius=12, fg_color='#ffffff', text_color='#2d3a4b', border_color='#b3d1ff',
            validate='key', validatecommand=(self.vcmd, '%P'))
        regis_entry_id.grid(row=1, column=1, sticky='w', padx=12)

        # Sex
        regis_label_sex = ctk.CTkLabel(self.register_frame, text='เพศ : ',
            font=('TH SarabunPSK', 20, 'bold'), text_color='#4a4a4a')
        regis_label_sex.grid(row=2, column=0, sticky='e', padx=12)
        regis_combo_sex = ctk.CTkOptionMenu(self.register_frame, values=['ชาย', 'หญิง'],
            font=('TH SarabunPSK', 20), dropdown_font=('TH SarabunPSK', 20),
            fg_color='#ffffff', button_color='#b3d1ff', text_color='#222')
        regis_combo_sex.grid(row=2, column=1, sticky='w', padx=12)

        # Name
        regis_label_name = ctk.CTkLabel(self.register_frame, text='ชื่อ : ',
            font=('TH SarabunPSK', 20, 'bold'), text_color='#4a4a4a')
        regis_label_name.grid(row=3, column=0, sticky='e', padx=12)
        regis_entry_name = ctk.CTkEntry(self.register_frame, font=('TH SarabunPSK', 20),
            width=220, border_width=2, corner_radius=12, fg_color='#ffffff', text_color='#2d3a4b', border_color='#b3d1ff')
        regis_entry_name.grid(row=3, column=1, sticky='w', padx=12)

        # Lastname
        regis_label_lname = ctk.CTkLabel(self.register_frame, text='นามสกุล : ',
            font=('TH SarabunPSK', 20, 'bold'), text_color='#4a4a4a')
        regis_label_lname.grid(row=4, column=0, sticky='e', padx=12)
        regis_entry_lname = ctk.CTkEntry(self.register_frame, font=('TH SarabunPSK', 20),
            width=220, border_width=2, corner_radius=12, fg_color='#ffffff', text_color='#2d3a4b', border_color='#b3d1ff')
        regis_entry_lname.grid(row=4, column=1, sticky='w', padx=12)

        # Lawsuit
        regis_label_lawsuit = ctk.CTkLabel(self.register_frame, text='คดี : ',
            font=('TH SarabunPSK', 20, 'bold'), text_color='#4a4a4a')
        regis_label_lawsuit.grid(row=5, column=0, sticky='e', padx=12)
        regis_entry_lawsuit = ctk.CTkTextbox(self.register_frame, font=('TH SarabunPSK', 20),
            width=220, height=60, border_width=2, corner_radius=12, fg_color='#ffffff', text_color='#2d3a4b', border_color='#b3d1ff')
        regis_entry_lawsuit.grid(row=5, column=1, sticky='w', padx=12)

        # Level
        regis_label_level = ctk.CTkLabel(self.register_frame, text='ชั้น : ',
            font=('TH SarabunPSK', 20, 'bold'), text_color='#4a4a4a')
        regis_label_level.grid(row=6, column=0, sticky='e', padx=12)
        regis_combo_level = ctk.CTkOptionMenu(self.register_frame,
            values=['ระหว่างพิจารณาคดี', 'เยี่ยม', 'ดีมาก', 'ดี', 'กลาง', 'ปรับปรุง', 'ปรับปรุงมาก'],
            font=('TH SarabunPSK', 20), dropdown_font=('TH SarabunPSK', 20),
            fg_color='#ffffff', button_color='#b3d1ff', text_color='#222')
        regis_combo_level.grid(row=6, column=1, sticky='w', padx=12)

        # Dan
        regis_label_dan = ctk.CTkLabel(self.register_frame, text='แดน : ',
            font=('TH SarabunPSK', 20, 'bold'), text_color='#4a4a4a')
        regis_label_dan.grid(row=7, column=0, sticky='e', padx=12)
        regis_combo_dan = ctk.CTkOptionMenu(self.register_frame,
            values=['1', '2', '3', '4', '5', '6', '7', 'รจช','รพ.นอก'],
            font=('TH SarabunPSK', 20), dropdown_font=('TH SarabunPSK', 20),
            fg_color='#ffffff', button_color='#b3d1ff', text_color='#222')
        regis_combo_dan.grid(row=7, column=1, sticky='w', padx=12)

        # Type
        regis_label_type = ctk.CTkLabel(self.register_frame, text='สถานะ : ',
            font=('TH SarabunPSK', 20, 'bold'), text_color='#4a4a4a')
        regis_label_type.grid(row=8, column=0, sticky='e', padx=12)
        regis_combo_type = ctk.CTkOptionMenu(self.register_frame,
            values=['ผู้ต้องขัง', 'ผู้ต้องกักขัง'],
            font=('TH SarabunPSK', 20), dropdown_font=('TH SarabunPSK', 20),
            fg_color='#ffffff', button_color='#b3d1ff', text_color='#222')
        regis_combo_type.grid(row=8, column=1, sticky='w', padx=12)

        # Buttons
        regis_button_submit = ctk.CTkButton(
            self.register_frame, text='บันทึกข้อมูล', width=120,
            font=('TH SarabunPSK', 20, 'bold'), fg_color='#4f8cff', hover_color='#2d3a4b',
            text_color='#fff', corner_radius=16, command=lambda: save_data_to_db()
        )
        regis_button_submit.grid(row=9, column=0, sticky='e', padx=12, pady=16)
        regis_button_clear = ctk.CTkButton(
            self.register_frame, text='ล้างข้อมูล', width=120,
            font=('TH SarabunPSK', 20, 'bold'), fg_color='#e3eefa', hover_color='#b3d1ff',
            text_color='#2d3a4b', corner_radius=16, command=lambda: clear_data()
        )
        regis_button_clear.grid(row=9, column=1, sticky='w', padx=12, pady=16)

        self.register_frame.grid_columnconfigure((0, 1), minsize=300)

        # ล้างข้อมูลในช่องกรอกข้อมูล
        def clear_data():
            regis_entry_id.delete(0,ctk.END)
            regis_combo_sex.set(value='')
            regis_entry_name.delete(0,ctk.END)
            regis_entry_lname.delete(0,ctk.END)
            regis_entry_lawsuit.delete('1.0','end')
            regis_combo_level.set(value='ระหว่างพิจารณาคดี')
            regis_combo_dan.set(value='1')
            regis_combo_type.set(value='ผู้ต้องขัง')

        # ส่งข้อมูลไป Database
        def save_data_to_db():
            print('1')
            data = [regis_entry_id.get().strip(),
                    regis_combo_sex.get().strip(),
                    regis_entry_name.get().strip(),
                    regis_entry_lname.get().strip(),
                    regis_entry_lawsuit.get("1.0", "end-1c").strip(),
                    regis_combo_level.get().strip(),
                    regis_combo_dan.get().strip(),
                    regis_combo_type.get().strip()]
            regis_button_submit.grid_forget()
            regis_button_clear.grid_forget()
            if not all(data):
                messagebox.showwarning('แจ้งเตือนการกรอกข้อมูล','กรุณากรอกข้อมูลให้ครบ')
                regis_button_submit.grid(row = 8,column = 0,sticky = 'e',padx = 5)
                regis_button_clear.grid(row = 8,column = 1,sticky = 'w',padx = 5)
                return
            # progressbar.grid(row = 8,column = 0,columnspan = 2,sticky = 'n',padx = 5)
            # progressbar.start()
            data.append('อยู่')
            result = self.db.add_data(data)
            if result == True:
                askmsg = messagebox.askyesno('แจ้งบันทึกข้อมูล','ต้องการเพิ่มผู้ต้องขังอีกหรือไม่')
                print('5')
                if askmsg == False:
                    print('6')
                    for widget in self.winfo_children():
                        widget.pack_forget()
                    clear_data()
                else:
                    print('7')
                    # progressbar.stop
                    # progressbar.grid_forget()
                    print('8')
                    regis_button_submit.grid(row = 8,column = 0,sticky = 'e',padx = 5)
                    regis_button_clear.grid(row = 8,column = 1,sticky = 'w',padx = 5)
                    print('9')
                    clear_data()
                    clear_data()
            else:
                messagebox.showerror('แจ้งการบันทึกข้อมูล','ไม่สามารถบันทึกข้อมูลได้กรุณาตรวจสอบใหม่')
                print('7')
                # progressbar.stop
                # progressbar.grid_forget()
                print('8')
                regis_button_submit.grid(row = 8,column = 0,sticky = 'e',padx = 5)
                regis_button_clear.grid(row = 8,column = 1,sticky = 'w',padx = 5)
                print('9')
                clear_data()

##############################################################################################################################################################################
#   ค้นหาผู้ต้องขังรายบุคคล
##############################################################################################################################################################################
    def search_one_prisoner(self):
        # แสดงข้อมูลจากการค้นหา 1 คน
        def show_one_prisoner():
            nonlocal prisoner_id_in_search_one
            nonlocal prisoner_name_in_search_one
            prison_id = search_one_var.get().strip()
            if showdata_entry_search.get() == '':
                messagebox.showerror('กรอกข้อมูล','กรุณากรอกข้อมูลในช่องค้นหา')
                return
            result_search_one = self.db.get_data_one(prison_id)
            if not result_search_one:
                messagebox.showerror('แจ้งเตือน',f'ไม่พบค่า {prison_id} ในฐานข้อมูล')
                showdata_entry_search.delete(0,ctk.END)
                return

            showdata_search_frame.grid(row = 3,column = 0,columnspan = 2,rowspan = 8,sticky = 'nsew')
            button_search.grid_forget()
            progressbar.grid(row = 2,column = 0,columnspan = 2)
            progressbar.start()


            showdata_id_data.configure(text = result_search_one[0])
            showdata_sex_data.configure(text = result_search_one[1])
            showdata_fname_data.configure(text = result_search_one[2])
            showdata_lname_data.configure(text = result_search_one[3])
            showdata_lawsuit_data.configure(text = result_search_one[4])
            showdata_level_data.configure(text = result_search_one[5])
            showdata_dan_data.configure(text = result_search_one[6])
            showdata_type.configure(text = result_search_one[7])
            showdata_status.configure(text = result_search_one[8])
            prisoner_id_in_search_one = result_search_one[0]
            prisoner_name_in_search_one = result_search_one[2] + ' ' + result_search_one[3]

            progressbar.stop()
            progressbar.grid_forget()
            button_search.grid(row = 2,column = 0,columnspan = 2)

            # ลงทะเบียนญาติ
        def register_relative():
            if showdata_id_data.cget('text') == '':
                messagebox.showerror(title='ข้อผิดพลาด',message='ไม่พบข้อมูลผู้ต้องขัง')
                return
            else:
                popup_register_relation = ctk.CTkToplevel(self)
                popup_register_relation.title('ลงทะเบียนญาติ')
                popup_register_relation.geometry('480x720+1+1')
                popup_register_relation.grab_set()
                popup_register_relation.configure(fg_color='#f4f7fa')  # เพิ่มสีพื้นหลังให้สอดคล้องกับธีม

                id_relative = ctk.StringVar()
                f_name_var = ctk.StringVar()
                l_name_var = ctk.StringVar()
                address_var = ctk.StringVar()
                tel_var = ctk.StringVar()
                frame_data_relative = ctk.CTkFrame(popup_register_relation, fg_color='#ffffff', corner_radius=16)  # เพิ่มสีและมุมมน
                for i in range(7):
                    frame_data_relative.grid_rowconfigure(i,weight=1,uniform='popup')
                # ตั้งค่า column
                for i in range(4):
                    popup_register_relation.grid_columnconfigure(i,weight=1,uniform='popup')
                    frame_data_relative.grid_columnconfigure(i,weight=1,uniform='popup')
                popup_register_relation.grid_rowconfigure(3,weight=1,uniform='popup')

                popup_label_content =ctk.CTkLabel(popup_register_relation,text='ลงทะเบียนญาติ',font=('TH SarabunPSK',28,'bold'),text_color='#2d3a4b')
                popup_label_content.grid(row = 0,column =0,columnspan = 4,pady = 10)

                popup_label_prisoner_id = ctk.CTkLabel(popup_register_relation,text='รหัสประจำตัว : ',font=('TH SarabunPSK',18,'bold'),text_color='#4a4a4a')
                popup_label_prisoner_id.grid(row = 1,column = 0,padx= 5,sticky = 'e',pady = 5)
                
                popup_label_prisoner_id_form_search_one = ctk.CTkLabel(popup_register_relation,text=prisoner_id_in_search_one,font=('TH SarabunPSK',18,'bold'),text_color='#2d3a4b')
                popup_label_prisoner_id_form_search_one.grid(row = 1,column = 1,padx= 5,sticky = 'w',pady = 5)

                popup_label_prisoner_name = ctk.CTkLabel(popup_register_relation,text='ชื่อ : ',font=('TH SarabunPSK',18,'bold'),text_color='#4a4a4a')
                popup_label_prisoner_name.grid(row = 1,column = 2,padx= 5,sticky = 'e',pady = 5)

                popup_label_prisoner_name_form_search_one = ctk.CTkLabel(popup_register_relation,text=prisoner_name_in_search_one,font=('TH SarabunPSK',18,'bold'),text_color='#2d3a4b')
                popup_label_prisoner_name_form_search_one.grid(row = 1,column = 3,padx= 5,sticky = 'w',pady = 5)

                popup_label_id_relative = ctk.CTkLabel(popup_register_relation,text='หมายเลขบัตรประชาชน',font=('TH SarabunPSK',18,'bold'),text_color='#4a4a4a')
                popup_label_id_relative.grid(row = 2,column = 0,columnspan = 2,padx= 5,sticky = 'e',pady = 5)

                popup_entry_id_relative = ctk.CTkEntry(popup_register_relation,font=('TH SarabunPSK',18),textvariable=id_relative,validate='key',validatecommand = (self.vcmd,'%P'),
                    fg_color='#ffffff', text_color='#2d3a4b', border_color='#4f8cff', border_width=2)
                popup_entry_id_relative.grid(row = 2,column = 2,padx= 5,sticky = 'w',pady = 5)

                popup_button_check_id = ctk.CTkButton(popup_register_relation,
                                                      text='ตรวจสอบ',
                                                      width=100,
                                                      font=('TH SarabunPSK',18,'bold'),
                                                      fg_color='#60bedb', hover_color='#3a7ca5', text_color='#ffffff',
                                                      command=lambda:check_relative_id())
                popup_button_check_id.grid(row=2 ,column = 3,padx= 5,sticky = 'w',pady = 5)

                popup_label_title_relative = ctk.CTkLabel(frame_data_relative,text='คำนำหน้า : ',font=('TH SarabunPSK',18,'bold'),text_color='#4a4a4a')
                popup_label_title_relative.grid(row = 0,column = 0,columnspan = 2,sticky = 'e',padx = 5)

                popup_combo_title_relative = ctk.CTkOptionMenu(frame_data_relative,values=['นาย','นาง','นางสาว','เด็กหญิง','เด็กชาย'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18),
                    fg_color='#ffffff', button_color='#4f8cff', text_color='#222')
                popup_combo_title_relative.grid(row = 0,column = 2,columnspan = 2,sticky = 'w',padx = 5)

                popup_label_fname_relative = ctk.CTkLabel(frame_data_relative,text='ชื่อ : ',font=('TH SarabunPSK',18,'bold'),text_color='#4a4a4a')
                popup_label_fname_relative.grid(row = 1,column = 0,columnspan = 2,padx= 5,sticky = 'e')

                popup_entry_fname_relative = ctk.CTkEntry(frame_data_relative,font=('TH SarabunPSK',18),textvariable=f_name_var,
                    fg_color='#ffffff', text_color='#2d3a4b', border_color='#4f8cff', border_width=2)
                popup_entry_fname_relative.grid(row = 1,column = 2,columnspan = 2,padx= 5,sticky = 'w')

                popup_label_lname_relative = ctk.CTkLabel(frame_data_relative,text='นามสกุล : ',font=('TH SarabunPSK',18,'bold'),text_color='#4a4a4a')
                popup_label_lname_relative.grid(row = 2,column = 0,columnspan = 2,padx= 2,sticky = 'e')

                popup_entry_lname_relative = ctk.CTkEntry(frame_data_relative,font=('TH SarabunPSK',18),textvariable=l_name_var,
                    fg_color='#ffffff', text_color='#2d3a4b', border_color='#4f8cff', border_width=2)
                popup_entry_lname_relative.grid(row = 2,column = 2,columnspan = 2,padx= 5,sticky = 'w')

                popup_label_address_relative = ctk.CTkLabel(frame_data_relative,text='ที่อยู่ : ',font=('TH SarabunPSK',18,'bold'),text_color='#4a4a4a')
                popup_label_address_relative.grid(row = 3,column = 0,columnspan = 2,padx= 5,sticky = 'e')

                popup_entry_address_relative = ctk.CTkEntry(frame_data_relative,font=('TH SarabunPSK',18),textvariable=address_var,
                    fg_color='#ffffff', text_color='#2d3a4b', border_color='#4f8cff', border_width=2)
                popup_entry_address_relative.grid(row = 3,column = 2,columnspan = 2,padx= 5,sticky = 'w')

                popup_label_tel_relative = ctk.CTkLabel(frame_data_relative,text='เบอร์โทร : ',font=('TH SarabunPSK',18,'bold'),text_color='#4a4a4a')
                popup_label_tel_relative.grid(row = 4,column = 0,columnspan = 2,padx= 5,sticky = 'e')

                popup_entry_tel_relative = ctk.CTkEntry(frame_data_relative,font=('TH SarabunPSK',18),textvariable=tel_var,validate='key',validatecommand = (self.vcmd,'%P'),
                    fg_color='#ffffff', text_color='#2d3a4b', border_color='#4f8cff', border_width=2)
                popup_entry_tel_relative.grid(row = 4,column = 2,columnspan = 2,padx= 5,sticky = 'w')

                popup_label_relation_relative = ctk.CTkLabel(frame_data_relative,text='ความสัมพันธ์ : ',font=('TH SarabunPSK',18,'bold'),text_color='#4a4a4a')
                popup_label_relation_relative.grid(row = 5,column = 0,columnspan = 2,padx= 5,sticky = 'e')
                popup_combo_relation_relative = ctk.CTkOptionMenu(frame_data_relative,values=['ปู่','ย่า','ตา','ยาย','ลุง','ป้า','พ่อ','แม่','น้า','พี่ชาย','พี่สาว','น้องชาย','น้องสาว','สามี','ภรรยา','ลูกสาว','ลูกชาย','อื่น ๆ'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18),
                    fg_color='#ffffff', button_color='#4f8cff', text_color='#222')
                popup_combo_relation_relative.grid(row = 5,column = 2,columnspan = 2,padx= 5,sticky = 'w')

                popup_button_submit = ctk.CTkButton(frame_data_relative,
                                                    text='บันทึกข้อมูล',
                                                    width=100,
                                                    font=('TH SarabunPSK',18,'bold'),
                                                    fg_color='#4f8cff', hover_color='#2d3a4b', text_color='#ffffff',
                                                    command=lambda:save_regis_relative_to_db()
                                                    )
                popup_button_cancel = ctk.CTkButton(frame_data_relative,
                                                    text='ยกเลิก',
                                                    width=100,
                                                    font=('TH SarabunPSK',18,'bold'),
                                                    fg_color='#ff4f4f', hover_color='#b30000', text_color='#ffffff',
                                                    command=lambda:clear_popup_regis()
                                                    )
                popup_button_submit.grid(row = 6,column = 0,padx = 5,columnspan = 2,sticky ='e' )
                popup_button_cancel.grid(row = 6,column = 2,padx = 5,columnspan = 2,sticky ='w' )

            def on_close():
                print('popup register ถูกปิด')
                showdata_entry_search.delete(0,tk.END)
                popup_register_relation.destroy()
                showdata_search_frame.grid_forget()

            def check_relative_id():
                if not id_relative.get():
                    messagebox.showerror('กรอกข้อมูล','ช่องค้นหาต้องไม่เป็นค่าว่าง')
                    return
                frame_data_relative.grid(row = 3,column = 0,columnspan = 4,sticky = 'nsew',padx = 5)
                result = self.db.get_data_for_ralative_id(popup_entry_id_relative.get().strip())
                if result != None:
                    popup_entry_id_relative.configure(state = 'disabled')
                    popup_combo_title_relative.set(result[1])
                    popup_combo_title_relative.configure(state = 'disabled')
                    f_name_var.set(result[2])
                    popup_entry_fname_relative.configure(state = 'disabled')
                    l_name_var.set(result[3])
                    popup_entry_lname_relative.configure(state = 'disabled')
                    address_var.set(result[4])
                    popup_entry_address_relative.configure(state = 'disabled')
                    tel_var.set(result[5])
                    popup_entry_tel_relative.configure(state = 'disabled')
                else:
                    popup_entry_id_relative.configure(state = 'disabled')

                    messagebox.showwarning('แจ้งเตือน',f'ไม่พบข้อมูลหมายเลข {popup_entry_id_relative.get().strip()} กรุณากรอกข้อมูลเพื่อลงทะเบียน')
                    popup_combo_title_relative.set('')
                    popup_combo_title_relative.configure(state = 'normal')
                    f_name_var.set('')
                    popup_entry_fname_relative.configure(state = 'normal')
                    l_name_var.set('')
                    popup_entry_lname_relative.configure(state = 'normal')
                    address_var.set('')
                    popup_entry_address_relative.configure(state = 'normal')
                    tel_var.set('')
                    popup_entry_tel_relative.configure(state = 'normal')

            def clear_popup_regis():
                frame_data_relative.grid_forget()
                popup_entry_id_relative.delete(0,ctk.END)
                popup_combo_title_relative.set('นาย')
                popup_entry_fname_relative.delete(0,ctk.END)
                popup_entry_lname_relative.delete(0,ctk.END)
                popup_entry_address_relative.delete(0,ctk.END)
                popup_entry_tel_relative.delete(0,ctk.END)
                popup_combo_relation_relative.set('')
                popup_combo_title_relative.set('')
                popup_combo_title_relative.configure(state = 'normal')
                f_name_var.set('')
                popup_entry_fname_relative.configure(state = 'normal')
                l_name_var.set('')
                popup_entry_lname_relative.configure(state = 'normal')
                address_var.set('')
                popup_entry_address_relative.configure(state = 'normal')
                tel_var.set('')
                popup_entry_tel_relative.configure(state = 'normal')
                popup_entry_id_relative.configure(state = 'normal')
                id_relative.set('')
            
            def save_regis_relative_to_db():
                showdata_entry_search.configure(state = 'normal')
                nonlocal prisoner_id_in_search_one
                prisoner_id = prisoner_id_in_search_one
                national_id_number = popup_entry_id_relative.get().strip()
                title = popup_combo_title_relative.get().strip()
                first_name = popup_entry_fname_relative.get().strip()
                last_name = popup_entry_lname_relative.get().strip()
                address = popup_entry_address_relative.get().strip()
                tel = popup_entry_tel_relative.get().strip()
                relation = popup_combo_relation_relative.get().strip()

                data = [national_id_number, title, first_name, last_name, address, tel]

                if not all(data) or not relation:
                    messagebox.showerror('แจ้งเตือน', 'กรุณากรอกข้อมูลให้ครบทุกช่อง')
                    return
                # ดึง SELECT prisoner_id,relative_id FROM relations WHERE prisoner_id = ?',(id,)
                print(prisoner_id,national_id_number)
                result = self.db.get_data_relation(prisoner_id)
                check_data = (prisoner_id, int(national_id_number))
                print(f'ตรวจสอบข้อมูล result = {result}')
                if not result:
                    print(not result)
                    # ส่งข้อมูลไปตารางญาติ 'INSERT INTO relatives (relative_id,title,f_name,l_name,address,tel)
                    result_db_relatives = self.db.add_data_ralative_to_relatives(prisoner_id,data,relation)
                    result_db_relations = self.db.add_data_relation_to_ralations(prisoner_id,data,relation)
                    continue_save = messagebox.askyesno('แจ้งเตือนการบันทึกข้อมูล',f'บันทึกข้อมูล "{popup_combo_title_relative.get().strip()}{popup_entry_fname_relative.get().strip()} {popup_entry_lname_relative.get().strip()}" สำเร็จ ต้องการเพิ่มญาติอีกหรือไม่')
                    if continue_save:
                        clear_popup_regis()
                        return
                    else:
                        on_close()
                        return

                # ตรวจสอบข้อมูลซ้ำ
                if check_data in result:
                    messagebox.showwarning('แจ้งข้อมูลซ้ำ',f'รหัสประจำตัวเลขที่ {national_id_number} มีการบันทึกข้อมูลแล้ว')
                    clear_popup_regis()
                    return
                
                if len(result) >=10:
                    messagebox.showwarning('ข้อมูลญาติ', 'ข้อมูลญาติเกิน 10 คน')
                    clear_popup_regis()
                    return
                
                # ถ้าไม่ซ้ำและยังไม่เกินจำนวน ให้บันทึกข้อมูล
                result_db_relatives = self.db.add_data_ralative_to_relatives(prisoner_id, data, relation)
                result_db_relations = self.db.add_data_relation_to_ralations(prisoner_id, data, relation)
                try:
                    continue_save = messagebox.askyesno('แจ้งเตือนการบันทึกข้อมูล',f'บันทึกข้อมูล "{popup_combo_title_relative.get().strip()}{popup_entry_fname_relative.get().strip()} {popup_entry_lname_relative.get().strip()}" สำเร็จ ต้องการเพิ่มญาติอีกหรือไม่')
                finally:
                    if continue_save:
                        clear_popup_regis()
                        frame_data_relative.grid_forget()
                    else:
                        on_close()
            popup_register_relation.protocol("WM_DELETE_WINDOW", on_close)

        # แสดงข้อมูลญาติ
        def show_list_relative():
            if showdata_id_data.cget('text') == '':
                messagebox.showerror(title='ข้อผิดพลาด',message='ไม่พบข้อมูลผู้ต้องขัง')
                return
            def resize_tree_columns():
                tree_container.update_idletasks()
                total_width = tree_container.winfo_width()
                for col, ratio in column_ratio.items():
                    tree.column(col,width=int(total_width * ratio),anchor='w')

            nonlocal prisoner_id_in_search_one
            nonlocal prisoner_name_in_search_one
            popup_show_list = ctk.CTkToplevel(self)
            popup_show_list.title('รายชื่อญาติ')
            popup_show_list.geometry('720x480+1+1')
            popup_show_list.grab_set()
            popup_show_list.configure(fg_color='#f4f7fa')  # เพิ่มสีพื้นหลังให้สอดคล้องกับธีม
            ctk.CTkLabel(popup_show_list,text=f'ข้อมูลญาติของ {prisoner_name_in_search_one}',font=('TH SarabunPSK',40,'bold')).grid(row = 0,column = 0,sticky = 'nsew')

            tree_container = ctk.CTkFrame(popup_show_list, fg_color='#ffffff', corner_radius=16)
            tree_container.grid(row = 2,column=0,padx=20, pady=10, sticky="nsew")

            tree_container.grid_rowconfigure(1,weight=1)
            tree_container.grid_columnconfigure(0,weight=1)
            popup_show_list.grid_rowconfigure(2, weight=1)
            popup_show_list.grid_columnconfigure(0, weight=1)

            # กำหนด style สำหรับ treeview 
            style = ttk.Style()
            style.theme_use('default')
            style.configure('Treeview',font =('TH SarabunPSK',18),rowheight = 35)
            style.configure('Treeview.Heading',font = ('TH SarabunPSK',18,'bold'))

            tree = ttk.Treeview(tree_container,columns=('relative_id','title','f_name','l_name','address','tel','relation'),show='headings',height=10)
            tree.heading('relative_id',text='รหัสประจำตัว')
            tree.heading('title',text='คำนำหน้า')
            tree.heading('f_name',text='ชื่อ')
            tree.heading('l_name',text='นามสกุล')
            tree.heading('address',text='ที่อยู่')
            tree.heading('tel',text='โทร')
            tree.heading('relation',text='ความสัมพันธ์')

            tree.column('relative_id',anchor='w')
            tree.column('title',anchor='w')
            tree.column('f_name',anchor='w')
            tree.column('l_name',anchor='w')
            tree.column('address',anchor='w')
            tree.column('tel',anchor='w')
            tree.column('relation',anchor='w')

            scrollbar = ttk.Scrollbar(tree_container,orient='vertical',command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            tree.grid(row=1,column=0,sticky='nsew')
            scrollbar.grid(row=1,column=1,sticky='ns')

            column_ratio ={
                        'relative_id' : 0.16,
                        'title' : 0.08,
                        'f_name' : 0.16,
                        'l_name' : 0.16,
                        'address' : 0.20,
                        'tel' : 0.12,
                        'relation' : 0.12
            }
            
            result = self.db.get_join_prisoners_and_relatives(prisoner_id_in_search_one)
            print(result)
            for row in result:
                tree.insert('','end',values=row)
            tree.bind('<Configure>',lambda e:resize_tree_columns())
            def on_close():
                print('ปิด show list')
                showdata_entry_search.delete(0,ctk.END)
                popup_show_list.destroy()
                showdata_search_frame.grid_forget()
            popup_show_list.protocol("WM_DELETE_WINDOW", on_close)


        self.showdata_frame.grid_columnconfigure((0,1),weight=1,uniform='showdata_frame')
        self.showdata_frame.grid_rowconfigure((0,1,2,3,4,5,6,7,8,9,10),weight=1,uniform='showdata_frame')

        prisoner_id_in_search_one = None
        prisoner_name_in_search_one = None
        search_one_var = tk.StringVar()
        
        progressbar = ctk.CTkProgressBar(self.register_frame,mode='indeterminate')

        showdata_label_content = ctk.CTkLabel(self.showdata_frame,text='ค้นหาผู้ต้องขัง',font=('TH SarabunPSK',40,'bold'), text_color='#2d3a4b')
        showdata_label_content.grid(row = 0,column = 0,columnspan = 2,sticky = 'nsew' , pady = 10)

        showdata_label_search = ctk.CTkLabel(self.showdata_frame,text='ระบุรหัสประจำตัวผู้ต้องขัง : ',font=('TH SarabunPSK',18,'bold'), text_color='#4a4a4a')
        showdata_label_search.grid(row = 1,column = 0,sticky = 'e',padx = 5)

        showdata_entry_search = ctk.CTkEntry(self.showdata_frame,textvariable=search_one_var,font=('TH SarabunPSK',18,'bold'),validate='key',validatecommand = (self.vcmd,'%P'),
            fg_color='#ffffff', text_color='#2d3a4b', border_color='#d4e6d4', border_width=2, corner_radius=12)
        showdata_entry_search.grid(row = 1,column = 1,sticky = 'w',padx = 5)

        button_search = ctk.CTkButton(self.showdata_frame,
                                      text='ค้นหาข้อมูลผู้ต้องขัง',
                                      font=('TH SarabunPSK',18,'bold'),
                                      fg_color='#4f8cff', hover_color='#2d3a4b', text_color='#ffffff',
                                      command=lambda:show_one_prisoner())
        button_search.grid(row = 2,column = 0,columnspan = 2)

        showdata_search_frame = ctk.CTkFrame(self.showdata_frame, fg_color='#ffffff', corner_radius=16, border_width=1, border_color='#d4e6d4')
        showdata_search_frame.grid_columnconfigure((1),weight=1)
        showdata_search_frame.grid_rowconfigure((0,1,2,3,4,5,6,7,8,9),weight=1)

        showdata_label_id = ctk.CTkLabel(showdata_search_frame,text='รหัสประจำตัว : ',font=('TH SarabunPSK',18,'bold'))
        showdata_label_id.grid(row = 0,column = 0,sticky = 'e',padx = 5)
        showdata_label_sex = ctk.CTkLabel(showdata_search_frame,text='เพศ : ',font=('TH SarabunPSK',18,'bold'))
        showdata_label_sex.grid(row = 1,column = 0,sticky = 'e',padx = 5)
        showdata_label_name = ctk.CTkLabel(showdata_search_frame,text='ชื่อ : ',font=('TH SarabunPSK',18,'bold'))
        showdata_label_name.grid(row = 2,column = 0,sticky = 'e',padx = 5)
        showdata_label_lname = ctk.CTkLabel(showdata_search_frame,text='นามสกุล : ',font=('TH SarabunPSK',18,'bold'))
        showdata_label_lname.grid(row = 3,column = 0,sticky = 'e',padx = 5)
        showdata_label_lawsuit = ctk.CTkLabel(showdata_search_frame,text='คดี : ',font=('TH SarabunPSK',18,'bold'))
        showdata_label_lawsuit.grid(row = 4,column = 0,sticky = 'e',padx = 5)
        showdata_label_level = ctk.CTkLabel(showdata_search_frame,text='ชั้น : ',font=('TH SarabunPSK',18,'bold'))
        showdata_label_level.grid(row = 5,column = 0,sticky = 'e',padx = 5)
        showdata_label_dan = ctk.CTkLabel(showdata_search_frame,text='แดน : ',font=('TH SarabunPSK',18,'bold'))
        showdata_label_dan.grid(row = 6,column = 0,sticky = 'e',padx = 5)
        showdata_label_type = ctk.CTkLabel(showdata_search_frame,text='ประเภท : ',font=('TH SarabunPSK',18,'bold'))
        showdata_label_type.grid(row = 7,column = 0,sticky = 'e',padx = 5)
        showdata_label_status = ctk.CTkLabel(showdata_search_frame,text='สถานะ : ',font=('TH SarabunPSK',18,'bold'))
        showdata_label_status.grid(row = 8,column = 0,sticky = 'e',padx = 5)
      
        showdata_id_data = ctk.CTkLabel(showdata_search_frame,text='',font=('TH SarabunPSK',18))
        showdata_id_data.grid(row = 0,column = 1,sticky = 'w',padx = 5)
        showdata_sex_data = ctk.CTkLabel(showdata_search_frame,text='',font=('TH SarabunPSK',18))
        showdata_sex_data.grid(row = 1,column = 1,sticky = 'w',padx = 5)
        showdata_fname_data = ctk.CTkLabel(showdata_search_frame,text='',font=('TH SarabunPSK',18))
        showdata_fname_data.grid(row = 2,column = 1,sticky = 'w',padx = 5)
        showdata_lname_data = ctk.CTkLabel(showdata_search_frame,text='',font=('TH SarabunPSK',18))
        showdata_lname_data.grid(row = 3,column = 1,sticky = 'w',padx = 5)
        showdata_lawsuit_data = ctk.CTkLabel(showdata_search_frame,text='',font=('TH SarabunPSK',18))
        showdata_lawsuit_data.grid(row = 4,column = 1 ,sticky = 'w',padx = 5)
        showdata_level_data = ctk.CTkLabel(showdata_search_frame,text='',font=('TH SarabunPSK',18))
        showdata_level_data.grid(row = 5,column = 1,sticky = 'w',padx = 5)
        showdata_dan_data = ctk.CTkLabel(showdata_search_frame,text='',font=('TH SarabunPSK',18))
        showdata_dan_data.grid(row = 6,column = 1,sticky = 'w',padx = 5)
        showdata_type = ctk.CTkLabel(showdata_search_frame,text='',font=('TH SarabunPSK',18))
        showdata_type.grid(row = 7,column = 1,sticky = 'w',padx = 5)
        showdata_status = ctk.CTkLabel(showdata_search_frame,text='',font=('TH SarabunPSK',18))
        showdata_status.grid(row = 8,column = 1,sticky = 'w',padx = 5)

        showdata_button_submit = ctk.CTkButton(showdata_search_frame,
                                                    text='เพิ่มญาติ',
                                                    width=100,
                                                    font=('TH SarabunPSK',18,'bold'),
                                                    command=lambda:register_relative())
        showdata_button_submit.grid(row = 9,column = 0,sticky = 'e',padx = 5)

        showdata_button_clear = ctk.CTkButton(showdata_search_frame,
                                                   text='รายชื่อญาติ',
                                                   width=100,
                                                   font=('TH SarabunPSK',18,'bold'),
                                                   command=lambda:show_list_relative())
        showdata_button_clear.grid(row = 9,column = 1,sticky = 'w',padx = 5)
        self.showdata_frame.grid_columnconfigure((0,1),minsize=200)

##############################################################################################################################################################################
#   ย้ายแดน และ ปรับชั้น
##############################################################################################################################################################################
    def move_and_adjust(self):

        def get_data_on_data_one():
            if not search_one_var.get():
                messagebox.showerror('','กรุณากรอกข้อมูลเพื่อค้นหา')
                return
            result = self.db.get_data_one(search_one_var.get())
            print(result)
            if not result:
                print('ไม่พบข้อมูล')
                messagebox.showerror('','ไม่พบข้อมูล กรุณาตรวจสอบรหัสประจำตัวผู้ต้องขัง')
                entry_search.delete(0,ctk.END)
                return
            search_frame.grid(row = 3 , column = 0 ,columnspan = 2 ,sticky = 'nsew')
            
            id_data.configure(text = result[0])
            sex_data.configure(text = result[1])
            fname_data.configure(text = result[2])
            lname_data.configure(text = result[3])
            lawsuit_data.configure(text = result[4])
            level_data.set(result[5])
            dan_data.set(result[6])
            type_data.set(result[7])
            status_data.set(result[8])

        def update_level_and_dan():
            id = id_data.cget('text')
            level = level_data.get()
            dan = dan_data.get()
            result =  self.db.update_level_and_dan(id,level,dan,type_data.get(),status_data.get())
            if result:
                messagebox.showinfo('แจ้งอัพเดทข้อมูล',f'อัพเดทข้อมูลของ {fname_data.cget('text')} {lname_data.cget('text')} สำเร็จ')
                entry_search.delete(0,tk.END)
                search_frame.grid_forget()

            else:
                messagebox.showerror('แจ้งอัพเดทข้อมูล',f'บันทึกข้อมูลไม่สำเร็จ')
        search_one_var = tk.StringVar()

        self.move_dan_and_adjust_level_frame.grid_columnconfigure((0,1),weight=1,uniform='move_adjust')
        self.move_dan_and_adjust_level_frame.grid_rowconfigure((3),weight=1,uniform='move_adjust')
 

        search_frame = ctk.CTkFrame(self.move_dan_and_adjust_level_frame, fg_color='#ffffff', corner_radius=16, border_width=1, border_color='#f4e6d4')

        label_content = ctk.CTkLabel(self.move_dan_and_adjust_level_frame,text='ย้ายแดน และ ปรับชั้น',font=('TH SarabunPSK',40,'bold'), text_color='#2d3a4b')
        label_content.grid(row = 0,column = 0,columnspan = 2,sticky = 'nsew' , pady = 10)

        label_search = ctk.CTkLabel(self.move_dan_and_adjust_level_frame,text='ระบุรหัสประจำตัวผู้ต้องขัง : ',font=('TH SarabunPSK',18,'bold'), text_color='#4a4a4a')
        label_search.grid(row = 1,column = 0,sticky = 'e',padx = 5,pady = 20)

        entry_search = ctk.CTkEntry(self.move_dan_and_adjust_level_frame,textvariable=search_one_var,font=('TH SarabunPSK',18,'bold'),validate='key',validatecommand = (self.vcmd,'%P'),
            fg_color='#ffffff', text_color='#2d3a4b', border_color='#f4e6d4', border_width=2, corner_radius=12)
        entry_search.grid(row = 1,column = 1,sticky = 'w',padx = 5,pady = 20)

        button_search = ctk.CTkButton(self.move_dan_and_adjust_level_frame,
                                      text='ค้นหาข้อมูลผู้ต้องขัง',
                                      font=('TH SarabunPSK',18,'bold'),
                                      fg_color='#ff8c4f', hover_color='#e67e22', text_color='#ffffff',
                                      command = lambda : get_data_on_data_one()
                                      )
        button_search.grid(row = 2,column = 0,columnspan = 2,pady = 20)

        # search_frame.grid(row = 3,column = 0,columnspan = 2,rowspan = 8,sticky = 'nsew')
        search_frame.grid_columnconfigure((1),weight=1,uniform='move_adjust')
        search_frame.grid_rowconfigure((0,1,2,3,4,5,6,7,8,9),weight=1,uniform='move_adjust')

        label_id = ctk.CTkLabel(search_frame,text='รหัสประจำตัว : ',font=('TH SarabunPSK',18,'bold'))
        label_id.grid(row = 0,column = 0,sticky = 'e',padx = 5)
        label_sex = ctk.CTkLabel(search_frame,text='เพศ : ',font=('TH SarabunPSK',18,'bold'))
        label_sex.grid(row = 1,column = 0,sticky = 'e',padx = 5)
        label_name = ctk.CTkLabel(search_frame,text='ชื่อ : ',font=('TH SarabunPSK',18,'bold'))
        label_name.grid(row = 2,column = 0,sticky = 'e',padx = 5)
        label_lname = ctk.CTkLabel(search_frame,text='นามสกุล : ',font=('TH SarabunPSK',18,'bold'))
        label_lname.grid(row = 3,column = 0,sticky = 'e',padx = 5)
        label_lawsuit = ctk.CTkLabel(search_frame,text='คดี : ',font=('TH SarabunPSK',18,'bold'))
        label_lawsuit.grid(row = 4,column = 0,sticky = 'e',padx = 5)
        label_level = ctk.CTkLabel(search_frame,text='ชั้น : ',font=('TH SarabunPSK',18,'bold'))
        label_level.grid(row = 5,column = 0,sticky = 'e',padx = 5)
        label_dan = ctk.CTkLabel(search_frame,text='แดน : ',font=('TH SarabunPSK',18,'bold'))
        label_dan.grid(row = 6,column = 0,sticky = 'e',padx = 5)
        label_type = ctk.CTkLabel(search_frame,text='ประเภท : ',font=('TH SarabunPSK',18,'bold'))
        label_type.grid(row = 7,column = 0,sticky = 'e',padx = 5)
        label_status = ctk.CTkLabel(search_frame,text='สถานะ : ',font=('TH SarabunPSK',18,'bold'))
        label_status.grid(row = 8,column = 0,sticky = 'e',padx = 5)
      
        id_data = ctk.CTkLabel(search_frame,text='',font=('TH SarabunPSK',18))
        sex_data = ctk.CTkLabel(search_frame,text='',font=('TH SarabunPSK',18))
        fname_data = ctk.CTkLabel(search_frame,text='',font=('TH SarabunPSK',18))
        lname_data = ctk.CTkLabel(search_frame,text='',font=('TH SarabunPSK',18))
        lawsuit_data = ctk.CTkLabel(search_frame,text='',font=('TH SarabunPSK',18))
        level_data = ctk.CTkOptionMenu(search_frame,values=['ระหว่างพิจารณาคดี','เยี่ยม','ดีมาก','ดี','กลาง','ปรับปรุง','ปรับปรุงมาก'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
        dan_data = ctk.CTkOptionMenu(search_frame,values=['1','2','3','4','5','6','7','รจช','รพ.นอก'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
        type_data = ctk.CTkOptionMenu(search_frame,values=['ผู้ต้องขัง','ผู้ต้องกักขัง'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
        status_data = ctk.CTkOptionMenu(search_frame,values=['อยู่','ไม่อยู่'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))

        id_data.grid(row = 0,column = 1,sticky = 'w',padx = 5)
        sex_data.grid(row = 1,column = 1,sticky = 'w',padx = 5)
        fname_data.grid(row = 2,column = 1,sticky = 'w',padx = 5)
        lname_data.grid(row = 3,column = 1,sticky = 'w',padx = 5)
        lawsuit_data.grid(row = 4,column = 1 ,sticky = 'w',padx = 5)
        level_data.grid(row = 5,column = 1,sticky = 'w',padx = 5)
        dan_data.grid(row = 6,column = 1,sticky = 'w',padx = 5)
        type_data.grid(row = 7,column = 1,sticky = 'w',padx = 5)
        status_data.grid(row = 8,column = 1,sticky = 'w',padx = 5)

        button_submit = ctk.CTkButton(search_frame,
                                                    text='บันทึกข้อมูล',
                                                    width=100,
                                                    font=('TH SarabunPSK',18,'bold'),
                                                    fg_color='#ff8c4f', hover_color='#e67e22', text_color='#ffffff',
                                                    command=lambda:update_level_and_dan()
                                                    )
        button_submit.grid(row = 9,column = 0,columnspan = 2,sticky = 'n',padx = 5)

        self.move_dan_and_adjust_level_frame.grid_columnconfigure((0,1),minsize=200)

##############################################################################################################################################################################
#   ค้นหาผู้ต้องขังทั้งหมด
##############################################################################################################################################################################
    def search_all_prisoner(self):

        def add_relative(prisoner_id, f_name, l_name):

            # Modern card-style popup
            popup_register_relation = ctk.CTkToplevel(self)
            popup_register_relation.title('ลงทะเบียนญาติ')
            popup_register_relation.geometry('550x520+1+1')
            popup_register_relation.grab_set()
            popup_register_relation.configure(fg_color="#ffffff", corner_radius=24, border_width=2, border_color="#e0e6ed")
            popup_register_relation.attributes("-topmost", True)
            popup_register_relation.transient(self)

            id_relative = ctk.StringVar()
            f_name_var = ctk.StringVar()
            l_name_var = ctk.StringVar()
            address_var = ctk.StringVar()
            tel_var = ctk.StringVar()

            # Header
            popup_label_content = ctk.CTkLabel(
                popup_register_relation,
                text='ลงทะเบียนญาติ',
                font=('TH SarabunPSK', 32, 'bold'),
                text_color='#2d3a4b'
            )
            popup_label_content.grid(row=0, column=0, columnspan=4, pady=(24, 10), sticky='n')

            # Prisoner info row
            ctk.CTkLabel(
                popup_register_relation, text='รหัสประจำตัว :', font=('TH SarabunPSK', 20, 'bold'), text_color='#4a4a4a'
            ).grid(row=1, column=0, padx=8, sticky='e', pady=5)
            ctk.CTkLabel(
                popup_register_relation, text=prisoner_id, font=('TH SarabunPSK', 20), text_color='#2d3a4b'
            ).grid(row=1, column=1, padx=8, sticky='w', pady=5)
            ctk.CTkLabel(
                popup_register_relation, text='ชื่อ :', font=('TH SarabunPSK', 20, 'bold'), text_color='#4a4a4a'
            ).grid(row=1, column=2, padx=8, sticky='e', pady=5)
            ctk.CTkLabel(
                popup_register_relation, text=f'{f_name} {l_name}', font=('TH SarabunPSK', 20), text_color='#2d3a4b'
            ).grid(row=1, column=3, padx=8, sticky='w', pady=5)

            # Card-style frame for form
            frame_data_relative = ctk.CTkFrame(
                popup_register_relation, fg_color="#f4f7fa", corner_radius=18, border_width=1, border_color="#e0e6ed"
            )
            for i in range(7):
                frame_data_relative.grid_rowconfigure(i, weight=1)
            for i in range(4):
                frame_data_relative.grid_columnconfigure(i, weight=1)

            # National ID
            ctk.CTkLabel(
                popup_register_relation, text='หมายเลขบัตรประชาชน', font=('TH SarabunPSK', 20, 'bold'), text_color='#4a4a4a'
            ).grid(row=2, column=0, columnspan=2, padx=8, sticky='e', pady=5)
            popup_entry_id_relative = ctk.CTkEntry(
                popup_register_relation, font=('TH SarabunPSK', 20), textvariable=id_relative,
                validate='key', validatecommand=(self.vcmd, '%P'), width=220, height=36,
                border_width=2, corner_radius=12, fg_color='#fff', text_color='#2d3a4b', border_color='#b3d1ff'
            )
            popup_entry_id_relative.grid(row=2, column=2, padx=8, sticky='w', pady=5)
            popup_entry_id_relative.bind('<Return>', lambda event: check_relative_id())
            ctk.CTkButton(
                popup_register_relation, text='ตรวจสอบ', width=100, height=36,
                font=('TH SarabunPSK', 20, 'bold'), fg_color='#4f8cff', hover_color='#2d3a4b', text_color='#fff',
                corner_radius=12, command=lambda: check_relative_id()
            ).grid(row=2, column=3, padx=8, sticky='w', pady=5)

            # Title
            ctk.CTkLabel(
                frame_data_relative, text='คำนำหน้า :', font=('TH SarabunPSK', 20, 'bold'), text_color='#4a4a4a'
            ).grid(row=0, column=0, columnspan=2, sticky='e', padx=8, pady=6)
            popup_combo_title_relative = ctk.CTkOptionMenu(
                frame_data_relative,
                values=['นาย','นาง','นางสาว','เด็กหญิง','เด็กชาย'],
                font=('TH SarabunPSK',18),
                dropdown_font=('TH SarabunPSK',18),
                fg_color='#fff', 
                button_color='#b3d1ff', 
                text_color='#222'
                )
            popup_combo_title_relative.grid(row=0, column=2, columnspan=2, sticky='w', padx=8, pady=6)

            # First name
            ctk.CTkLabel(
                frame_data_relative, text='ชื่อ :', font=('TH SarabunPSK', 20, 'bold'), text_color='#4a4a4a'
            ).grid(row=1, column=0, columnspan=2, padx=8, sticky='e', pady=6)
            popup_entry_fname_relative = ctk.CTkEntry(
                frame_data_relative, font=('TH SarabunPSK', 20), textvariable=f_name_var,
                width=220, height=36, border_width=2, corner_radius=12, fg_color='#fff', text_color='#2d3a4b', border_color='#b3d1ff'
            )
            popup_entry_fname_relative.grid(row=1, column=2, columnspan=2, padx=8, sticky='w', pady=6)

            # Last name
            ctk.CTkLabel(
                frame_data_relative, text='นามสกุล :', font=('TH SarabunPSK', 20, 'bold'), text_color='#4a4a4a'
            ).grid(row=2, column=0, columnspan=2, padx=8, sticky='e', pady=6)
            popup_entry_lname_relative = ctk.CTkEntry(
                frame_data_relative, font=('TH SarabunPSK', 20), textvariable=l_name_var,
                width=220, height=36, border_width=2, corner_radius=12, fg_color='#fff', text_color='#2d3a4b', border_color='#b3d1ff'
            )
            popup_entry_lname_relative.grid(row=2, column=2, columnspan=2, padx=8, sticky='w', pady=6)

            # Address
            ctk.CTkLabel(
                frame_data_relative, text='ที่อยู่ :', font=('TH SarabunPSK', 20, 'bold'), text_color='#4a4a4a'
            ).grid(row=3, column=0, columnspan=2, padx=8, sticky='e', pady=6)
            popup_entry_address_relative = ctk.CTkEntry(
                frame_data_relative, font=('TH SarabunPSK', 20), textvariable=address_var,
                width=220, height=36, border_width=2, corner_radius=12, fg_color='#fff', text_color='#2d3a4b', border_color='#b3d1ff'
            )
            popup_entry_address_relative.grid(row=3, column=2, columnspan=2, padx=8, sticky='w', pady=6)

            # Tel
            ctk.CTkLabel(
                frame_data_relative, text='เบอร์โทร :', font=('TH SarabunPSK', 20, 'bold'), text_color='#4a4a4a'
            ).grid(row=4, column=0, columnspan=2, padx=8, sticky='e', pady=6)
            popup_entry_tel_relative = ctk.CTkEntry(
                frame_data_relative, font=('TH SarabunPSK', 20), textvariable=tel_var,
                validate='key', validatecommand=(self.vcmd, '%P'),
                width=220, height=36, border_width=2, corner_radius=12, fg_color='#fff', text_color='#2d3a4b', border_color='#b3d1ff'
            )
            popup_entry_tel_relative.grid(row=4, column=2, columnspan=2, padx=8, sticky='w', pady=6)

            # Relation
            ctk.CTkLabel(
                frame_data_relative, text='ความสัมพันธ์ :', font=('TH SarabunPSK', 20, 'bold'), text_color='#4a4a4a'
            ).grid(row=5, column=0, columnspan=2, padx=8, sticky='e', pady=6)
            popup_combo_relation_relative = ctk.CTkOptionMenu(
                frame_data_relative, values=['ปู่', 'ย่า', 'ตา', 'ยาย', 'ลุง', 'ป้า', 'พ่อ', 'แม่', 'น้า', 'พี่ชาย', 'พี่สาว', 'น้องชาย', 'น้องสาว', 'สามี', 'ภรรยา', 'ลูกสาว', 'ลูกชาย', 'อื่น ๆ'],
                font=('TH SarabunPSK', 20), dropdown_font=('TH SarabunPSK', 20),
                fg_color='#fff', button_color='#b3d1ff', text_color='#222', width=120
            )
            popup_combo_relation_relative.grid(row=5, column=2, columnspan=2, padx=8, sticky='w', pady=6)

            # Buttons
            popup_button_submit = ctk.CTkButton(
                frame_data_relative, text='บันทึกข้อมูล', width=120, height=38,
                font=('TH SarabunPSK', 20, 'bold'), fg_color='#4f8cff', hover_color='#2d3a4b', text_color='#fff',
                corner_radius=14, command=lambda: save_regis_relative_to_db()
            )
            popup_button_cancel = ctk.CTkButton(
                frame_data_relative, text='ยกเลิก', width=120, height=38,
                font=('TH SarabunPSK', 20, 'bold'), fg_color='#e3eefa', hover_color='#b3d1ff', text_color='#2d3a4b',
                corner_radius=14, command=lambda: clear_popup_regis()
            )
            popup_button_submit.grid(row=6, column=0, padx=8, columnspan=2, sticky='e', pady=(16, 12))
            popup_button_cancel.grid(row=6, column=2, padx=8, columnspan=2, sticky='w', pady=(16, 12))

            def on_close():
                popup_register_relation.destroy()

            def check_relative_id():
                try:
                    self.thai_id_reader.read_card()
                    info = self.thai_id_reader.get_person_info()
                    id_relative.set(info['cid'])
                except Exception as e:
                    messagebox.showerror('ข้อผิดพลาด', 'ไม่สามารถอ่านบัตรประชาชนได้ กรุณากรอกข้อมูลด้วยตนเอง')
                    pass
                if not id_relative.get():
                    messagebox.showerror('กรอกข้อมูล', 'ช่องค้นหาต้องไม่เป็นค่าว่าง')
                    return
                frame_data_relative.grid(row=3, column=0, columnspan=4, sticky='nsew', padx=18, pady=(10, 0))
                result = self.db.get_data_for_ralative_id(popup_entry_id_relative.get().strip())
                if result is not None:

                    frame_data_relative.grid(row=3, column=0, columnspan=4, padx=18, pady=(10, 0), sticky='nsew')
                    popup_entry_id_relative.configure(state='disabled')
                    popup_combo_title_relative.set(result[1])
                    popup_combo_title_relative.configure(state='disabled')
                    f_name_var.set(result[2])
                    popup_entry_fname_relative.configure(state='disabled')
                    l_name_var.set(result[3])
                    popup_entry_lname_relative.configure(state='disabled')
                    address_var.set(result[4])
                    popup_entry_address_relative.configure(state='disabled')
                    tel_var.set(result[5])
                    popup_entry_tel_relative.configure(state='disabled')
                else:
                    popup_entry_id_relative.configure(state='disabled')
                    frame_data_relative.grid(row=3, column=0, columnspan=4, padx=18, pady=(10, 0), sticky='nsew')

                    try:
                        popup_combo_title_relative.set(info['title'])
                        popup_combo_title_relative.configure(state='normal')
                        f_name_var.set(info['firstname'])
                        popup_entry_fname_relative.configure(state='normal')
                        l_name_var.set(info['lastname'])
                        popup_entry_lname_relative.configure(state='normal')
                        address_var.set(info['address'])
                        popup_entry_address_relative.configure(state='normal')
                        tel_var.set('')
                        popup_entry_tel_relative.configure(state='normal')
                    except:
                        popup_combo_title_relative.set('')
                        popup_combo_title_relative.configure(state='normal')
                        f_name_var.set('')
                        popup_entry_fname_relative.configure(state='normal')
                        l_name_var.set('')
                        popup_entry_lname_relative.configure(state='normal')
                        address_var.set('')
                        popup_entry_address_relative.configure(state='normal')
                        tel_var.set('')
                        popup_entry_tel_relative.configure(state='normal')
                        pass

            def clear_popup_regis():
                popup_entry_id_relative.configure(state='normal')
                popup_entry_id_relative.delete(0, ctk.END)
                popup_combo_title_relative.set('')
                popup_combo_title_relative.configure(state='normal')
                f_name_var.set('')
                popup_entry_fname_relative.configure(state='normal')
                l_name_var.set('')
                popup_entry_lname_relative.configure(state='normal')
                address_var.set('')
                popup_entry_address_relative.configure(state='normal')
                tel_var.set('')
                popup_entry_tel_relative.configure(state='normal')
                popup_combo_relation_relative.set('')
                id_relative.set('')
                frame_data_relative.grid_forget()


            def save_regis_relative_to_db():
                national_id_number = popup_entry_id_relative.get().strip()
                title = popup_combo_title_relative.get().strip()
                first_name = popup_entry_fname_relative.get().strip()
                last_name = popup_entry_lname_relative.get().strip()
                address = popup_entry_address_relative.get().strip()
                tel = popup_entry_tel_relative.get().strip()
                relation = popup_combo_relation_relative.get().strip()

                data = [national_id_number, title, first_name, last_name, address, tel]

                if not all(data) or not relation:
                    messagebox.showerror('แจ้งเตือน', 'กรุณากรอกข้อมูลให้ครบทุกช่อง')
                    return
                result = self.db.get_data_relation(prisoner_id)
                check_data = (prisoner_id, int(national_id_number))
                if not result:
                    result_db_relatives = self.db.add_data_ralative_to_relatives(prisoner_id, data, relation)
                    result_db_relations = self.db.add_data_relation_to_ralations(prisoner_id, data, relation)
                    continue_save = messagebox.askyesno('แจ้งเตือนการบันทึกข้อมูล', f'บันทึกข้อมูล "{popup_combo_title_relative.get().strip()}{popup_entry_fname_relative.get().strip()} {popup_entry_lname_relative.get().strip()}" สำเร็จ ต้องการเพิ่มญาติอีกหรือไม่')
                    if continue_save:
                        clear_popup_regis()
                        return
                    else:
                        on_close()
                        return
                if check_data in result:
                    messagebox.showwarning('แจ้งข้อมูลซ้ำ', f'รหัสประจำตัวเลขที่ {national_id_number} มีการบันทึกข้อมูลแล้ว')
                    clear_popup_regis()
                    return
                if len(result) >= 10:
                    messagebox.showwarning('ข้อมูลญาติ','ข้อมูลญาติเกิน 10 คน')
                    clear_popup_regis()
                    return
                result_db_relatives = self.db.add_data_ralative_to_relatives(prisoner_id, data, relation)
                result_db_relations = self.db.add_data_relation_to_ralations(prisoner_id, data, relation)
                try:
                    continue_save = messagebox.askyesno('แจ้งเตือนการบันทึกข้อมูล', f'บันทึกข้อมูล "{popup_combo_title_relative.get().strip()}{popup_entry_fname_relative.get().strip()} {popup_entry_lname_relative.get().strip()}" สำเร็จ ต้องการเพิ่มญาติอีกหรือไม่')
                finally:
                    if continue_save:
                        clear_popup_regis()
                    else:
                        on_close()

            popup_register_relation.protocol("WM_DELETE_WINDOW", on_close)

        def show_relative(prisoner_id, f_name, l_name):
            def get_join_prisoners_and_relatives_alldata():
                return self.db.get_join_prisoners_and_relatives_alldata(prisoner_id)
            # print('show_relative fn')
            def resize_tree_columns():
                tree_container_relative.update_idletasks()
                total_width = tree_container_relative.winfo_width()
                for col, ratio in column_ratio.items():
                    tree_relative.column(col,width=int(total_width * ratio),anchor='w')

            def on_close():
                print('ปิด show list')
                popup_show_list.destroy()

            def show_menu_delete_relation(event):
                selected = tree_relative.identify_row(event.y)
                if not selected:
                    return
            
                tree_relative.selection_set(selected)
                relative = tree_relative.item(selected)['values']
                relative_id = relative[0]
                relative_name = f'{relative[2]} {relative[3]}'
                popup_window_delete_relative = ctk.CTkToplevel(popup_show_list)  # ✅ set parent เป็น popup_show_list
                popup_window_delete_relative.overrideredirect(True)
                popup_window_delete_relative.geometry(f"+{event.x_root}+{event.y_root}")
                popup_window_delete_relative.configure(fg_color="#f0f0f0")
                popup_window_delete_relative.attributes("-topmost", True)
                popup_window_delete_relative.transient(popup_show_list)
                popup_window_delete_relative.lift()
            
                def delete_rel():
                    popup_window_delete_relative.destroy()
                    print("ลบ:", prisoner_id, relative_id)
                    confirm_delete = messagebox.askyesno('การลบข้อมูล', f'ต้องการลบข้อมูลของ {relative_name} หรือไม่')
                    if confirm_delete:
                        result_delete = self.db.delete_relation_from_prisoner_and_relative(prisoner_id, relative_id)
                        if result_delete:
                            messagebox.showinfo('ลบข้อมูล', 'ลบข้อมูลของเสร็จสิ้น')
                            result = self.db.get_join_prisoners_and_relatives_alldata(prisoner_id)
                            print(result)
                            for row in tree_relative.get_children():
                                tree_relative.delete(row)
                            for row in result:
                                tree_relative.insert('', 'end', values=row)
            
                def edit_rel():
                    def on_close_edit_rel():
                        edit_relative_window.destroy()
                        result = get_join_prisoners_and_relatives_alldata()
                        print(result)
                        for row in tree_relative.get_children():
                            tree_relative.delete(row)
                        for row in result:
                            tree_relative.insert('', 'end', values=row)

                    def get_relation():
                        get_relation_data = self.db.get_relation(prisoner_id,relative_id)
                        return get_relation_data if get_relation_data else None
                    
                    def save_edit_relative():
                        result_save_edit_relative = self.db.edit_relation(relation_edit.get(),relative_id, prisoner_id)
                        if result_save_edit_relative:
                            alert = ALERT(edit_relative_window, [f'บันทึกความสัมพันธ์ของผู้ต้องขัง\n{f_name} {l_name}\nสำเร็จ'],button=True)
                            if alert.show():
                                on_close_edit_rel()
                                return
                            return
                        else:
                            alert = ALERT(edit_relative_window, [f'บันทึกความสัมพันธ์ของผู้ต้องขัง\n{f_name} {l_name}\nไม่สำเร็จ'],button=True)
                            return

                    popup_window_delete_relative.destroy()
                    print("แก้ไข:", prisoner_id, relative_id)
                    print(f'{result[0][1]}{result[0][2]} {result[0][3]}')
                    edit_relative_window = ctk.CTkToplevel(popup_show_list)
                    edit_relative_window.title('แก้ไขควาสมสัมพันธ์')
                    edit_relative_window.geometry('550x520+1+1')
                    edit_relative_window.grab_set()
                    edit_relative_window.configure(fg_color="#ffffff", corner_radius=24, border_width=2, border_color="#e0e6ed")
                    edit_relative_window.attributes("-topmost", True)
                    edit_relative_window.transient(popup_show_list)

                    frame_edit_relative = ctk.CTkFrame(
                        edit_relative_window, fg_color="#f4f7fa", corner_radius=18, border_width=1, border_color="#e0e6ed"
                    )
                    frame_edit_relative.pack(padx=10, pady=10, fill='both', expand=True)

                    frame_edit_relative.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
                    frame_edit_relative.grid_columnconfigure((0, 1), weight=1)

                    ctk.CTkLabel(
                        frame_edit_relative, text='แก้ไขข้อมูลความสัมพันธ์', font=('TH SarabunPSK', 32, 'bold'), text_color='#2d3a4b'
                    ).grid(row=0, column=0, columnspan=2, pady=(24, 10), sticky='n')

                    ctk.CTkLabel(
                        frame_edit_relative, text='ชื่อญาติ :', font=('TH SarabunPSK', 24, 'bold'), text_color='#4a4a4a'
                    ).grid(row=1, column=0, padx=8, sticky='e', pady=5)
                    ctk.CTkLabel(
                        frame_edit_relative, text=f'{result[0][1]}{result[0][2]} {result[0][3]}', font=('TH SarabunPSK', 24), text_color='#2d3a4b'
                    ).grid(row=1, column=1, padx=8, sticky='w', pady=5)
                    ctk.CTkLabel(
                        frame_edit_relative, text='ความสัมพันธ์เป็น :', font=('TH SarabunPSK', 24, 'bold'), text_color='#4a4a4a'
                    ).grid(row=2, column=0, padx=8, sticky='e', pady=5)

                    relation_edit = ctk.CTkOptionMenu(
                        frame_edit_relative, values=['ปู่','ย่า','ตา','ยาย','ลุง','ป้า','พ่อ','แม่','น้า','พี่ชาย','พี่สาว','น้องชาย','น้องสาว','สามี','ภรรยา','ลูกสาว','ลูกชาย','อื่น ๆ'],
                        font=('TH SarabunPSK', 20), dropdown_font=('TH SarabunPSK', 24),
                        fg_color='#fff', button_color='#b3d1ff', text_color='#222'
                    )
                    relation_edit.grid(row=2, column=1, padx=8, sticky='w', pady=5)
                    relation_edit.set(get_relation() if get_relation() else '')
                    ctk.CTkLabel(
                        frame_edit_relative, text='ของ', font=('TH SarabunPSK', 24, 'bold'), text_color='#4a4a4a'
                    ).grid(row=3, column=0,columnspan = 2, padx=8, sticky='ew', pady=5)
                    ctk.CTkLabel(
                        frame_edit_relative, text='ชื่อผู้ต้องขัง :', font=('TH SarabunPSK', 24, 'bold'), text_color='#4a4a4a'
                    ).grid(row=4, column=0, padx=8, sticky='e', pady=5)
                    ctk.CTkLabel(
                        frame_edit_relative, text=f'{f_name} {l_name}', font=('TH SarabunPSK', 24), text_color='#2d3a4b'
                    ).grid(row=4, column=1, padx=8, sticky='w', pady=5)

                    ctk.CTkButton(
                        frame_edit_relative, text='บันทึกการแก้ไข', width=120, height=38,
                        font=('TH SarabunPSK', 20, 'bold'), fg_color='#4f8cff', hover_color='#2d3a4b', text_color='#fff',
                        corner_radius=14, command=lambda: save_edit_relative()
                    ).grid(row=5, column=0, padx=8, columnspan=2, sticky='n', pady=(16, 12))
                    
                    edit_relative_window.protocol("WM_DELETE_WINDOW", lambda:on_close_edit_rel())

            
                ctk.CTkButton(
                    popup_window_delete_relative,
                    text='แก้ไขความสัมพันธ์',
                    font=('TH SarabunPSK', 18, 'bold'),
                    width=120,
                    command=edit_rel
                ).pack(padx=10, pady=(5, 10))

                ctk.CTkButton(
                    popup_window_delete_relative,
                    text='ลบรายชื่อญาติ',
                    font=('TH SarabunPSK', 18, 'bold'),
                    width=120,
                    command=delete_rel
                ).pack(padx=10, pady=(10, 5))
            
                # ✅ ให้โฟกัสหลังจากเปิด (ป้องกัน focus ไม่ติด)
                popup_window_delete_relative.after(100, lambda: popup_window_delete_relative.focus_force())
                popup_window_delete_relative.bind("<FocusOut>", lambda e: popup_window_delete_relative.destroy())

            popup_show_list = ctk.CTkToplevel(self)
            popup_show_list.title('รายชื่อญาติ')
            popup_show_list.geometry('960x680+1+1')
            popup_show_list.grab_set()
            popup_show_list.configure(fg_color='#f4f7fa')  # เพิ่มสีพื้นหลังให้สอดคล้องกับธีม
            popup_show_list.attributes("-topmost", True)
            popup_show_list.transient(self)

            ctk.CTkLabel(popup_show_list,text=f'ข้อมูลญาติของ {f_name} {l_name}',font=('TH SarabunPSK',40,'bold')).grid(row = 0,column = 0,sticky = 'nsew')

            tree_container_relative = ctk.CTkFrame(popup_show_list)
            tree_container_relative.grid(row = 2,column=0,padx=20, pady=10, sticky="nsew")

            tree_container_relative.grid_rowconfigure(1,weight=1)
            tree_container_relative.grid_columnconfigure(0,weight=1)
            popup_show_list.grid_rowconfigure(2, weight=1)
            popup_show_list.grid_columnconfigure(0, weight=1)

            tree_relative = ttk.Treeview(tree_container_relative,columns=('relative_id','title','f_name','l_name','address','tel','relation'),show='headings',height=10)
            tree_relative.heading('relative_id',text='รหัสประจำตัว')
            tree_relative.heading('title',text='คำนำหน้า')
            tree_relative.heading('f_name',text='ชื่อ')
            tree_relative.heading('l_name',text='นามสกุล')
            tree_relative.heading('address',text='ที่อยู่')
            tree_relative.heading('tel',text='โทร')
            tree_relative.heading('relation',text='ความสัมพันธ์')

            tree_relative.column('relative_id',anchor='w')
            tree_relative.column('title',anchor='w')
            tree_relative.column('f_name',anchor='w')
            tree_relative.column('l_name',anchor='w')
            tree_relative.column('address',anchor='w')
            tree_relative.column('tel',anchor='w')
            tree_relative.column('relation',anchor='w')

            # scrollbar = ttk.Scrollbar(tree_container_relative,orient='vertical',command=tree.yview)
            # tree_relative.configure(yscrollcommand=scrollbar.set)
            tree_relative.grid(row=1,column=0,sticky='nsew')
            # scrollbar.grid(row=1,column=1,sticky='ns')

            column_ratio ={
                        'relative_id' : 0.16,
                        'title' : 0.08,
                        'f_name' : 0.16,
                        'l_name' : 0.16,
                        'address' : 0.20,
                        'tel' : 0.12,
                        'relation' : 0.12
            }
            print('prisoner_id = ',prisoner_id)
            result = get_join_prisoners_and_relatives_alldata()
            print('in show_relative ',result)
            
            for row in result:
                tree_relative.insert('','end',values=row)

            popup_window_delete_relative = None
            tree_relative.bind('<Configure>',lambda e:resize_tree_columns())
            if user_session.is_admin():
                tree_relative.bind("<Button-3>", show_menu_delete_relation)
            popup_show_list.protocol("WM_DELETE_WINDOW", on_close)

        def move_dan_and_adjust_level(prisoner_id):
            def get_data_on_data_one():
                result = self.db.get_data_one(prisoner_id)
                print(result)
                id_data.configure(text = result[0])
                sex_data.set(result[1])
                fname_data.delete(0,ctk.END)
                fname_data.insert(0,result[2])
                lname_data.delete(0,ctk.END)
                lname_data.insert(0,result[3])
                lawsuit_data.delete("1.0", ctk.END)
                lawsuit_data.insert("1.0", result[4])
                level_data.set(result[5])
                dan_data.set(result[6])
                type_data.set(result[7])
                status_data.set(result[8])
                disciplinary_data.set(result[9])
                
            def update_level_and_dan():
                id = id_data.cget('text')
                sex = sex_data.get()
                f_name = fname_data.get().strip()
                l_name = lname_data.get().strip()
                lawsuit = lawsuit_data.get("1.0", ctk.END).strip()
                level = level_data.get()
                dan = dan_data.get()
                result =  self.db.update_level_and_dan(id,sex,f_name,l_name,lawsuit,level,dan,type_data.get(),status_data.get(),disciplinary_data.get())
                if result:
                    messagebox.showinfo('แจ้งอัพเดทข้อมูล',f'อัพเดทข้อมูลของ {f_name} {l_name} สำเร็จ')
                    load_data_on_db()
                    on_close()
                    return
                else:
                    messagebox.showerror('แจ้งอัพเดทข้อมูล',f'บันทึกข้อมูลไม่สำเร็จ')

            def on_close():
                print('ปิด Move Dan')
                popup_move_dan.destroy()

            popup_move_dan = ctk.CTkToplevel(self)
            
            popup_move_dan.title('ย้ายแดน')
            popup_move_dan.geometry('480x720+1+1')
            popup_move_dan.grab_set()
            popup_move_dan.configure(fg_color='#f4f7fa')  # เพิ่มสีพื้นหลังให้สอดคล้องกับธีม

            search_frame = ctk.CTkFrame(popup_move_dan, fg_color='#ffffff', corner_radius=16)  # เพิ่มสีและมุมมน
            search_frame.pack(fill='both',expand = True, padx=20, pady=20)  # เพิ่ม padding

            search_frame.grid_columnconfigure((0,1),weight=1,uniform='move_adjust',minsize=100)
            search_frame.grid_rowconfigure((0,1,2,3,4,5,6,7,8,9,10,11),weight=1,uniform='move_adjust')

            label_content = ctk.CTkLabel(search_frame,text='ย้ายแดน และ ปรับชั้น',font=('TH SarabunPSK',40,'bold'))
            label_content.grid(row = 0,column = 0,columnspan = 2,sticky = 'nsew' , pady = 10)
            
            label_id = ctk.CTkLabel(search_frame,text='รหัสประจำตัว : ',font=('TH SarabunPSK',18,'bold'))
            label_id.grid(row = 1,column = 0,sticky = 'e',padx = 5)
            label_sex = ctk.CTkLabel(search_frame,text='เพศ : ',font=('TH SarabunPSK',18,'bold'))
            label_sex.grid(row = 2,column = 0,sticky = 'e',padx = 5)
            label_name = ctk.CTkLabel(search_frame,text='ชื่อ : ',font=('TH SarabunPSK',18,'bold'))
            label_name.grid(row = 3,column = 0,sticky = 'e',padx = 5)
            label_lname = ctk.CTkLabel(search_frame,text='นามสกุล : ',font=('TH SarabunPSK',18,'bold'))
            label_lname.grid(row = 4,column = 0,sticky = 'e',padx = 5)
            label_lawsuit = ctk.CTkLabel(search_frame,text='คดี : ',font=('TH SarabunPSK',18,'bold'))
            label_lawsuit.grid(row = 5,column = 0,sticky = 'e',padx = 5)
            label_level = ctk.CTkLabel(search_frame,text='ชั้น : ',font=('TH SarabunPSK',18,'bold'))
            label_level.grid(row = 6,column = 0,sticky = 'e',padx = 5)
            label_dan = ctk.CTkLabel(search_frame,text='แดน : ',font=('TH SarabunPSK',18,'bold'))
            label_dan.grid(row = 7,column = 0,sticky = 'e',padx = 5)
            label_type = ctk.CTkLabel(search_frame,text='ประเภท : ',font=('TH SarabunPSK',18,'bold'))
            label_type.grid(row = 8,column = 0,sticky = 'e',padx = 5)
            label_status = ctk.CTkLabel(search_frame,text='สถานะ : ',font=('TH SarabunPSK',18,'bold'))
            label_status.grid(row = 9,column = 0,sticky = 'e',padx = 5)
            label_disciplinary = ctk.CTkLabel(search_frame,text='วินัย : ',font=('TH SarabunPSK',18,'bold'))
            label_disciplinary.grid(row = 10,column = 0,sticky = 'e',padx = 5)
        
            id_data = ctk.CTkLabel(search_frame,text='',font=('TH SarabunPSK',18))
            sex_data = ctk.CTkOptionMenu(search_frame,values=['ชาย','หญิง'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
            fname_data = ctk.CTkEntry(search_frame,font=('TH SarabunPSK',18))
            lname_data = ctk.CTkEntry(search_frame,font=('TH SarabunPSK',18))
            lawsuit_data = ctk.CTkTextbox(search_frame,font=('TH SarabunPSK',18),height=60)
            level_data = ctk.CTkOptionMenu(search_frame,values=['ระหว่างพิจารณาคดี','เยี่ยม','ดีมาก','ดี','กลาง','ปรับปรุง','ปรับปรุงมาก'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
            dan_data = ctk.CTkOptionMenu(search_frame,values=['1','2','3','4','5','6','7','รจช','รพ.นอก'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
            type_data = ctk.CTkOptionMenu(search_frame,values=['ผู้ต้องขัง','ผู้ต้องกักขัง'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
            status_data = ctk.CTkOptionMenu(search_frame,values=['อยู่','ไม่อยู่'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
            disciplinary_data = ctk.CTkOptionMenu(search_frame,values=['ไม่มี','ผิดวินัย'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))

            id_data.grid(row = 1,column = 1,sticky = 'w',padx = 5)
            sex_data.grid(row = 2,column = 1,sticky = 'w',padx = 5)
            fname_data.grid(row = 3,column = 1,sticky = 'w',padx = 5)
            lname_data.grid(row = 4,column = 1,sticky = 'w',padx = 5)
            lawsuit_data.grid(row = 5,column = 1 ,sticky = 'w',padx = 5)
            level_data.grid(row = 6,column = 1,sticky = 'w',padx = 5)
            dan_data.grid(row = 7,column = 1,sticky = 'w',padx = 5)
            type_data.grid(row = 8,column = 1,sticky = 'w',padx = 5)
            status_data.grid(row = 9,column = 1,sticky = 'w',padx = 5)
            disciplinary_data.grid(row = 10,column = 1,sticky = 'w',padx = 5)

            button_submit = ctk.CTkButton(
                search_frame,
                text='บันทึกข้อมูล',
                width=100,
                font=('TH SarabunPSK',18,'bold'),
                command=lambda:update_level_and_dan()
                )
            
            button_submit.grid(row = 11,column = 0,columnspan = 2,sticky = 'n',padx = 5)

            popup_move_dan.grid_columnconfigure((0,1),minsize=200)
            get_data_on_data_one()
            popup_move_dan.protocol("WM_DELETE_WINDOW", on_close)

            #############################################################################

        # insert ข้อมูลให้อยู่ในตาราง treeview
        def show_prisoners(data):
            for row in tree.get_children():
                tree.delete(row)
            
            # Check if data is valid and iterable
            if data and isinstance(data, (list, tuple)):
                for row in data:
                    tree.insert('','end',values=row)
            else:
                print("Warning: ข้อมูลไม่ถูกต้องหรือเป็นค่าว่าง")

        # ค้นหาข้อมูลจากตาราง และกรองตามเงื่อนไขต่างๆ
        def search_and_filter_prisoners():
            nonlocal all_data
            keyword = search_all_var.get().lower()
            
            # Check if all_data is valid before filtering
            if not all_data or not isinstance(all_data, list):
                print("Warning: ไม่มีข้อมูลสำหรับการค้นหา")
                show_prisoners([])
                return
            
            # Start with all data
            filtered = all_data.copy()
            
            # Filter by search keyword (name)
            if keyword:
                filtered = [
                    row for row in filtered 
                    if len(row) > 3 and (keyword in str(row[2]).lower() or keyword in str(row[3]).lower())
                ]
            
            # Filter by level (ชั้น) - index 5
            selected_levels = [level for level, var in level_filters.items() if var.get()]
            if selected_levels:
                filtered = [row for row in filtered if len(row) > 5 and row[5] in selected_levels]
            
            # Filter by dan (แดน) - index 6
            selected_dans = [dan for dan, var in dan_filters.items() if var.get()]
            if selected_dans:
                filtered = [row for row in filtered if len(row) > 6 and row[6] in selected_dans]
            
            # Filter by type (ประเภท) - index 7
            selected_types = [type_val for type_val, var in type_filters.items() if var.get()]
            if selected_types:
                filtered = [row for row in filtered if len(row) > 7 and row[7] in selected_types]
            
            # Filter by status (สถานะ) - index 8
            selected_statuses = [status for status, var in status_filters.items() if var.get()]
            if selected_statuses:
                filtered = [row for row in filtered if len(row) > 8 and row[8] in selected_statuses]
            
            # Filter by disciplinary (ผิดวินัย) - index 9
            selected_disciplinaries = [disc for disc, var in disciplinary_filters.items() if var.get()]
            if selected_disciplinaries:
                filtered = [row for row in filtered if len(row) > 9 and row[9] in selected_disciplinaries]
            
            show_prisoners(filtered)

        def resize_tree_columns():
            tree_container.update_idletasks()
            total_width = tree_container.winfo_width()
            for col, ratio in column_ratios.items():
                tree.column(col,width=int(total_width * ratio),anchor='w')

        def load_data_on_db():
            nonlocal all_data
            all_data = []
            print(f"กำลังโหลดข้อมูลจากฐานข้อมูล: {self.db.db_path}")
            
            if not self.db.db_path or not os.path.exists(self.db.db_path):
                print(f"Error: ไม่พบไฟล์ฐานข้อมูล: {self.db.db_path}")
                messagebox.showerror("ข้อผิดพลาด", f"ไม่พบไฟล์ฐานข้อมูล:\n{self.db.db_path}")
                show_prisoners([])
                return
                
            data_result = self.db.get_data_all()
            print(f"ผลลัพธ์จาก get_data_all: {type(data_result)}, จำนวน: {len(data_result) if isinstance(data_result, list) else 'N/A'}")
            
            if isinstance(data_result, list):
                all_data = data_result
                print(f"โหลดข้อมูลสำเร็จ: {len(all_data)} รายการ")
                show_prisoners(all_data)
            else:
                print("Error: ไม่สามารถโหลดข้อมูลได้")
                all_data = []
                show_prisoners(all_data)
                messagebox.showwarning("คำเตือน", "ไม่สามารถโหลดข้อมูลจากฐานข้อมูลได้\nกรุณาตรวจสอบการเชื่อมต่อฐานข้อมูล")


        # Modernize the main frame
        self.show_all_prisoner_frame.configure(fg_color="#ffffff", corner_radius=24)
        self.show_all_prisoner_frame.grid_rowconfigure(3, weight=1)  # Changed from 2 to 3 for new filter row
        self.show_all_prisoner_frame.grid_columnconfigure(0, weight=1)

        search_all_var = tk.StringVar()
        
        # Initialize filter variables
        level_filters = {}
        dan_filters = {}
        type_filters = {}
        status_filters = {}
        disciplinary_filters = {}
        
        # Level options
        level_options = ['ระหว่างพิจารณาคดี','เยี่ยม','ดีมาก','ดี','กลาง','ปรับปรุง','ปรับปรุงมาก']
        for level in level_options:
            level_filters[level] = tk.BooleanVar()
        
        # Dan options
        dan_options = ['1','2','3','4','5','6','7','รจช']
        for dan in dan_options:
            dan_filters[dan] = tk.BooleanVar()
        
        # Type options
        type_options = ['ผู้ต้องขัง','ผู้ต้องกักขัง']
        for type_val in type_options:
            type_filters[type_val] = tk.BooleanVar()
        
        # Status options
        status_options = ['อยู่','ไม่อยู่']
        for status in status_options:
            status_filters[status] = tk.BooleanVar()
        
        # Disciplinary options
        disciplinary_options = ['ไม่มี','ผิดวินัย']
        for disc in disciplinary_options:
            disciplinary_filters[disc] = tk.BooleanVar()

        # Header
        ctk.CTkLabel(
            self.show_all_prisoner_frame,
            text='ผู้ต้องขังทั้งหมด',
            font=('TH SarabunPSK', 44, 'bold'),
            text_color='#2d3a4b'
        ).grid(row=0, column=0, pady=(24, 10), sticky='n')

        # Search box
        search_entry = ctk.CTkEntry(
            self.show_all_prisoner_frame,
            placeholder_text='พิมพ์ชื่อเพื่อค้นหา...',
            font=('TH SarabunPSK', 20),
            width=260,
            border_width=2,
            corner_radius=12,
            fg_color='#f4f7fa',
            text_color='#2d3a4b',
            border_color='#b3d1ff',
            height=36,
            textvariable=search_all_var
        )
        search_entry.grid(row=1, column=0, pady=(0, 16), sticky='n')
        search_all_var.trace_add("write", lambda *args: search_and_filter_prisoners())

        # Filter Controls Frame
        filter_frame = ctk.CTkFrame(
            self.show_all_prisoner_frame,
            fg_color="#f4f7fa",
            corner_radius=18,
            border_width=2,
            border_color="#e0e6ed"
        )
        filter_frame.grid(row=2, column=0, padx=24, pady=(0, 12), sticky="ew")
        
        # Configure filter frame grid
        filter_frame.grid_columnconfigure(0, weight=1)
        filter_frame.grid_columnconfigure(1, weight=1)
        filter_frame.grid_columnconfigure(2, weight=1)
        filter_frame.grid_columnconfigure(3, weight=1)
        filter_frame.grid_columnconfigure(4, weight=1)

        # Filter header
        filter_header = ctk.CTkLabel(
            filter_frame,
            text='🔍 กรองข้อมูล',
            font=('TH SarabunPSK', 24, 'bold'),
            text_color='#2d3a4b'
        )
        filter_header.grid(row=0, column=0, columnspan=5, pady=(12, 8), sticky='n')

        # Level Filter
        level_frame = ctk.CTkFrame(filter_frame, fg_color="#ffffff", corner_radius=12)
        level_frame.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(level_frame, text='ชั้น', font=('TH SarabunPSK', 18, 'bold'), text_color='#2d3a4b').pack(pady=(8, 4))
        
        # Create 2-column layout for level checkboxes
        level_checkbox_frame = ctk.CTkFrame(level_frame, fg_color="transparent")
        level_checkbox_frame.pack(fill='both', expand=True, padx=8, pady=4)
        level_checkbox_frame.grid_columnconfigure(0, weight=1)
        level_checkbox_frame.grid_columnconfigure(1, weight=1)
        
        for i, level in enumerate(level_options):
            col = i % 2  # Alternate between column 0 and 1
            row = i // 2  # Calculate row position
            checkbox = ctk.CTkCheckBox(level_checkbox_frame, text=level, variable=level_filters[level], 
                                     command=search_and_filter_prisoners, font=('TH SarabunPSK', 14))
            checkbox.grid(row=row, column=col, sticky='w', padx=4, pady=1)

        # Dan Filter
        dan_frame = ctk.CTkFrame(filter_frame, fg_color="#ffffff", corner_radius=12)
        dan_frame.grid(row=1, column=1, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(dan_frame, text='แดน', font=('TH SarabunPSK', 18, 'bold'), text_color='#2d3a4b').pack(pady=(8, 4))
        
        # Create 2-column layout for dan checkboxes
        dan_checkbox_frame = ctk.CTkFrame(dan_frame, fg_color="transparent")
        dan_checkbox_frame.pack(fill='both', expand=True, padx=8, pady=4)
        dan_checkbox_frame.grid_columnconfigure(0, weight=1)
        dan_checkbox_frame.grid_columnconfigure(1, weight=1)
        
        for i, dan in enumerate(dan_options):
            col = i % 2  # Alternate between column 0 and 1
            row = i // 2  # Calculate row position
            checkbox = ctk.CTkCheckBox(dan_checkbox_frame, text=dan, variable=dan_filters[dan], 
                                     command=search_and_filter_prisoners, font=('TH SarabunPSK', 14))
            checkbox.grid(row=row, column=col, sticky='w', padx=4, pady=1)

        # Type Filter
        type_frame = ctk.CTkFrame(filter_frame, fg_color="#ffffff", corner_radius=12)
        type_frame.grid(row=1, column=2, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(type_frame, text='ประเภท', font=('TH SarabunPSK', 18, 'bold'), text_color='#2d3a4b').pack(pady=(8, 4))
        
        # Create 2-column layout for type checkboxes
        type_checkbox_frame = ctk.CTkFrame(type_frame, fg_color="transparent")
        type_checkbox_frame.pack(fill='both', expand=True, padx=8, pady=4)
        type_checkbox_frame.grid_columnconfigure(0, weight=1)
        type_checkbox_frame.grid_columnconfigure(1, weight=1)
        
        for i, type_val in enumerate(type_options):
            col = i % 2  # Alternate between column 0 and 1
            row = i // 2  # Calculate row position
            checkbox = ctk.CTkCheckBox(type_checkbox_frame, text=type_val, variable=type_filters[type_val], 
                                     command=search_and_filter_prisoners, font=('TH SarabunPSK', 14))
            checkbox.grid(row=row, column=col, sticky='w', padx=4, pady=1)

        # Status Filter
        status_frame = ctk.CTkFrame(filter_frame, fg_color="#ffffff", corner_radius=12)
        status_frame.grid(row=1, column=3, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(status_frame, text='สถานะ', font=('TH SarabunPSK', 18, 'bold'), text_color='#2d3a4b').pack(pady=(8, 4))
        
        # Create 2-column layout for status checkboxes
        status_checkbox_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_checkbox_frame.pack(fill='both', expand=True, padx=8, pady=4)
        status_checkbox_frame.grid_columnconfigure(0, weight=1)
        status_checkbox_frame.grid_columnconfigure(1, weight=1)
        
        for i, status in enumerate(status_options):
            col = i % 2  # Alternate between column 0 and 1
            row = i // 2  # Calculate row position
            checkbox = ctk.CTkCheckBox(status_checkbox_frame, text=status, variable=status_filters[status], 
                                     command=search_and_filter_prisoners, font=('TH SarabunPSK', 14))
            checkbox.grid(row=row, column=col, sticky='w', padx=4, pady=1)

        # Disciplinary Filter
        disciplinary_frame = ctk.CTkFrame(filter_frame, fg_color="#ffffff", corner_radius=12)
        disciplinary_frame.grid(row=1, column=4, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(disciplinary_frame, text='ผิดวินัย', font=('TH SarabunPSK', 18, 'bold'), text_color='#2d3a4b').pack(pady=(8, 4))
        
        # Create 2-column layout for disciplinary checkboxes
        disciplinary_checkbox_frame = ctk.CTkFrame(disciplinary_frame, fg_color="transparent")
        disciplinary_checkbox_frame.pack(fill='both', expand=True, padx=8, pady=4)
        disciplinary_checkbox_frame.grid_columnconfigure(0, weight=1)
        disciplinary_checkbox_frame.grid_columnconfigure(1, weight=1)
        
        for i, disc in enumerate(disciplinary_options):
            col = i % 2  # Alternate between column 0 and 1
            row = i // 2  # Calculate row position
            checkbox = ctk.CTkCheckBox(disciplinary_checkbox_frame, text=disc, variable=disciplinary_filters[disc], 
                                     command=search_and_filter_prisoners, font=('TH SarabunPSK', 14))
            checkbox.grid(row=row, column=col, sticky='w', padx=4, pady=1)

        # Clear All Filters Button
        clear_filters_btn = ctk.CTkButton(
            filter_frame,
            text='🗑️ ล้างตัวกรองทั้งหมด',
            font=('TH SarabunPSK', 16, 'bold'),
            fg_color='#ff6b6b',
            hover_color='#ff5252',
            text_color='#ffffff',
            width=180,
            height=32,
            corner_radius=12,
            command=lambda: clear_all_filters()
        )
        clear_filters_btn.grid(row=2, column=0, columnspan=5, pady=(8, 12))

        def clear_all_filters():
            # Clear all filter checkboxes
            for var in level_filters.values():
                var.set(False)
            for var in dan_filters.values():
                var.set(False)
            for var in type_filters.values():
                var.set(False)
            for var in status_filters.values():
                var.set(False)
            for var in disciplinary_filters.values():
                var.set(False)
            
            # Refresh the display
            search_and_filter_prisoners()

        # Card-style container for table
        tree_container = ctk.CTkFrame(
            self.show_all_prisoner_frame,
            fg_color="#f4f7fa",
            corner_radius=18,
            border_width=2,
            border_color="#e0e6ed"
        )
        tree_container.grid(row=3, column=0, padx=24, pady=12, sticky="nsew")  # Changed from row=2 to row=3
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        # Modern Treeview style
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Treeview',
            font=('TH SarabunPSK', 18),
            rowheight=30,
            background="#f4f7fa",
            fieldbackground="#f4f7fa",
            borderwidth=0,
            relief="flat"
        )
        style.configure('Treeview.Heading',
            font=('TH SarabunPSK', 20, 'bold'),
            background="#e3eefa",
            foreground="#2d3a4b",
            borderwidth=0
        )
        style.map('Treeview', background=[('selected', '#b3d1ff')])

        # Modern Scrollbar style - เหมือน CTkScrollableFrame
        style.configure('Custom.Vertical.TScrollbar',
            gripcount=0,
            background="#e3eefa",        # scrollbar_fg_color
            darkcolor="#e3eefa", 
            lightcolor="#e3eefa",
            troughcolor="#e3eefa",       # scrollbar_fg_color
            bordercolor="#e3eefa",
            borderwidth=0,
            relief="flat",
            arrowcolor="#b3d1ff",        # scrollbar_button_color
            arrowsize=12,
            width=16                     # ปรับความกว้างของ scrollbar
        )
        
        # Configure scrollbar thumb (ส่วนที่ลากได้)
        style.configure('Custom.Vertical.TScrollbar.thumb',
            relief="flat",
            background="#b3d1ff",        # scrollbar_button_color
            bordercolor="#b3d1ff",
            borderwidth=0
        )
        
        # Map สำหรับ hover effects เหมือน CTkScrollableFrame
        style.map('Custom.Vertical.TScrollbar',
            background=[('active', '#b3d1ff'), ('pressed', '#2d3a4b')],  # scrollbar_button_hover_color
            arrowcolor=[('active', '#2d3a4b'), ('pressed', '#ffffff')],
            relief=[('pressed', 'flat'), ('!pressed', 'flat')]
        )
        
        # Map สำหรับ thumb hover effects
        style.map('Custom.Vertical.TScrollbar.thumb',
            background=[('active', '#2d3a4b'), ('pressed', '#2d3a4b')],  # scrollbar_button_hover_color
            relief=[('pressed', 'flat'), ('!pressed', 'flat')]
        )

        tree = ttk.Treeview(
            tree_container,
            columns=('prisoner_id','sex','f_name','l_name','lawsuit','level','dan','type','status','disciplinary'),
            show='headings',
            height=12,
            style='Treeview'
        )
        tree.heading('prisoner_id', text='รหัสประจำตัว')
        tree.heading('sex', text='เพศ')
        tree.heading('f_name', text='ชื่อ')
        tree.heading('l_name', text='นามสกุล')
        tree.heading('lawsuit', text='คดี')
        tree.heading('level', text='ชั้น')
        tree.heading('dan', text='แดน')
        tree.heading('type', text='ประเภท')
        tree.heading('status', text='สถานะ')
        tree.heading('disciplinary', text='ผิดวินัย')

        # Set column width and alignment
        tree.column('prisoner_id', anchor='center', width=100, minwidth=80, stretch=True)
        tree.column('sex', anchor='center', width=60, minwidth=50, stretch=True)
        tree.column('f_name', anchor='w', width=120, minwidth=80, stretch=True)
        tree.column('l_name', anchor='w', width=120, minwidth=80, stretch=True)
        tree.column('lawsuit', anchor='w', width=200, minwidth=120, stretch=True)
        tree.column('level', anchor='center', width=80, minwidth=60, stretch=True)
        tree.column('dan', anchor='center', width=60, minwidth=50, stretch=True)
        tree.column('type', anchor='center', width=100, minwidth=80, stretch=True)
        tree.column('status', anchor='center', width=100, minwidth=80, stretch=True)
        tree.column('disciplinary', anchor='center', width=100, minwidth=80, stretch=True)

        # Modern vertical scrollbar with CTkScrollableFrame styling
        scrollbar = ttk.Scrollbar(tree_container, orient='vertical', command=tree.yview, style='Custom.Vertical.TScrollbar')
        tree.configure(yscrollcommand=scrollbar.set)
        tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns', padx=(0, 4), pady=8)

        column_ratios = {
            'prisoner_id': 0.10,
            'sex': 0.04,
            'f_name': 0.11,
            'l_name': 0.11,
            'lawsuit': 0.18,
            'level': 0.09,
            'dan': 0.06,
            'type': 0.11,
            'status': 0.10,
            'disciplinary': 0.1
        }

        # ฟังก์ชันสำหรับแสดงเมนูคลิกขวา
        def show_ctk_popup(event):
            # ล้าง popup เก่าถ้ามี
            nonlocal popup_window
            try:
                popup_window.destroy()
            except:
                pass

            # เลือกแถวใน Treeview
            selected = tree.identify_row(event.y)
            if not selected:
                return
            tree.selection_set(selected)
            values = tree.item(selected)['values']
            if not values:
                return

            prisoner_id = values[0]
            f_name = values[2]
            l_name = values[3]

            # Modern card-style popup window
            popup_window = ctk.CTkToplevel()
            popup_window.overrideredirect(True)
            popup_window.geometry(f"+{event.x_root}+{event.y_root}")
            popup_window.configure(fg_color="#ffffff", corner_radius=18, border_width=2, border_color="#e0e6ed")
            popup_window.attributes("-topmost", True)

            # Header (optional, for clarity)
            header = ctk.CTkLabel(
                popup_window,
                text=f"{f_name} {l_name}",
                font=("TH SarabunPSK", 22, "bold"),
                text_color="#2d3a4b"
            )
            header.pack(padx=16, pady=(14, 6))

            # Button style
            btn_kwargs = dict(
                font=("TH SarabunPSK", 20, "bold"),
                width=180,
                height=38,
                corner_radius=12
            )

            def add_rel():
                popup_window.destroy()
                add_relative(prisoner_id, f_name, l_name)

            def show_rel():
                popup_window.destroy()
                show_relative(prisoner_id, f_name, l_name)

            def move_dan():
                popup_window.destroy()
                move_dan_and_adjust_level(prisoner_id)

            def delete_rel():
                popup_window.destroy()
                confirm_delete = messagebox.askyesno('ยืนยันลบข้อมูล', f'ลบข้อมูลของ {f_name} {l_name}')
                if confirm_delete:
                    result_delete = self.db.delete_prisoner(prisoner_id)
                    if result_delete:
                        messagebox.showinfo('ลบข้อมูล', 'ลบข้อมูลเสร็จสิ้น')
                        load_data_on_db()
                    else:
                        messagebox.showerror('ลบข้อมูล', 'ลบข้อมูลไม่สำเร็จ')

            # Modern buttons
            if user_session.is_admin():
                ctk.CTkButton(
                    popup_window, text="➕ เพิ่มญาติ", fg_color="#4f8cff", hover_color="#2d3a4b", text_color="#fff",
                    command=add_rel, **btn_kwargs
                ).pack(padx=18, pady=(8, 4))

            ctk.CTkButton(
                popup_window, text="👥 ดูรายชื่อญาติ", fg_color="#e3eefa", hover_color="#b3d1ff", text_color="#2d3a4b",
                command=show_rel, **btn_kwargs
            ).pack(padx=18, pady=4)

            ctk.CTkButton(
                popup_window, text="➡️ แก้ไขข้อมูลผู้ต้องขัง", fg_color="#e3eefa", hover_color="#b3d1ff", text_color="#2d3a4b",
                command=move_dan, **btn_kwargs
            ).pack(padx=18, pady=4)

            if user_session.is_admin():
                ctk.CTkButton(
                    popup_window, text="🗑️ ลบผู้ต้องขัง", fg_color="#ff4f4f", hover_color="#b30000", text_color="#fff",
                    command=delete_rel, **btn_kwargs
                ).pack(padx=18, pady=(4, 14))

            # Shadow effect (optional, for modern look)
            # popup_window.attributes('-alpha', 0.98)

            # ปิด popup เมื่อ focus หลุด
            popup_window.bind("<FocusOut>", lambda e: popup_window.destroy())
            popup_window.focus_set()

        # ฟังก์ชันสำหรับ Ctrl + คลิกขวา เพื่อคัดลอกข้อมูล
        def show_copy_menu(event):
            nonlocal popup_copy_window
            # ปิดเมนูคัดลอกเก่าหากมี
            try:
                popup_copy_window.destroy()
            except:
                pass

            # ระบุแถวที่คลิก
            selected = tree.identify_row(event.y)
            if not selected:
                return "break"

            tree.selection_set(selected)
            values = tree.item(selected).get('values')
            if not values or len(values) < 4:
                return "break"

            prisoner_id = str(values[0])
            f_name = str(values[2])
            l_name = str(values[3])

            # สร้าง popup เมนูแบบ modern
            popup_copy_window = ctk.CTkToplevel()
            popup_copy_window.overrideredirect(True)
            popup_copy_window.geometry(f"+{event.x_root}+{event.y_root}")
            popup_copy_window.configure(fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#e0e6ed")
            popup_copy_window.attributes("-topmost", True)

            btn_kwargs = dict(
                font=("TH SarabunPSK", 18, "bold"),
                width=220,
                height=36,
                corner_radius=10
            )

            def copy_only_id():
                try:
                    self.clipboard_clear()
                    self.clipboard_append(prisoner_id)
                finally:
                    popup_copy_window.destroy()

            def copy_full_name():
                try:
                    self.clipboard_clear()
                    self.clipboard_append(f"{f_name} {l_name}")
                finally:
                    popup_copy_window.destroy()

            ctk.CTkButton(
                popup_copy_window,
                text="คัดลอกเฉพาะ รหัสประจำตัว",
                fg_color="#4f8cff",
                hover_color="#2d3a4b",
                text_color="#fff",
                command=copy_only_id,
                **btn_kwargs
            ).pack(padx=12, pady=(10, 6))

            ctk.CTkButton(
                popup_copy_window,
                text="คัดลอกชื่อ + นามสกุล",
                fg_color="#e3eefa",
                hover_color="#b3d1ff",
                text_color="#2d3a4b",
                command=copy_full_name,
                **btn_kwargs
            ).pack(padx=12, pady=(0, 10))

            popup_copy_window.bind("<FocusOut>", lambda e: popup_copy_window.destroy())
            popup_copy_window.focus_set()

            # ป้องกันไม่ให้เมนูคลิกขวาปกติแสดงซ้อน
            return "break"

        # ผูกกับคลิกขวา
        tree.bind("<Button-3>", show_ctk_popup)
        # ผูก Ctrl + คลิกขวา สำหรับเมนูคัดลอกข้อมูล
        tree.bind("<Control-Button-3>", show_copy_menu)
        tree.bind('<Configure>',lambda e:resize_tree_columns())
        popup_window = None
        popup_copy_window = None
        all_data = []
        load_data_on_db()

##############################################################################################################################################################################
#   ญาติทั้งหมด
##############################################################################################################################################################################
    def search_all_relatives(self):

        # menu right click
        def on_right_click(event):
            nonlocal popup_window_all_relative
            try:
                popup_window_all_relative.destroy()
            except:
                pass

            # เลือกแถวในตาราง tree
            selected = tree.identify_row(event.y)
            if not selected:
                return
            
            tree.selection_set(selected)
            values = tree.item(selected)['values']
            if not values:
                return
            
            relative_id = values[0]
            relative_name = f'{values[2]} {values[3]}'
        
            popup_window_all_relative = ctk.CTkToplevel()
            popup_window_all_relative.overrideredirect(True)
            popup_window_all_relative.geometry(f'+{event.x_root}+{event.y_root}')
            popup_window_all_relative.configure(fg_color='#f8fbff', corner_radius=10, border_width=2, border_color='#4f8cff')

            def show_rel():
                popup_window_all_relative.destroy()
                print(relative_id,relative_name)
                show_relative(relative_id,relative_name)

            def edit_rel():
                popup_window_all_relative.destroy()
                edit_relative(relative_id)

            ctk.CTkButton(popup_window_all_relative,text='ดูรายชื่อผุ้ต้องขัง',font =('TH SarabunPSK',18,'bold'),command=show_rel,width=160,
                fg_color='#4f8cff', hover_color='#2d3a4b', text_color='#ffffff').pack(padx = 10,pady = (10,5))
            ctk.CTkButton(popup_window_all_relative,text='แก้ไขข้อมูล',font =('TH SarabunPSK',18,'bold'),command=edit_rel,width=160,
                fg_color='#60bedb', hover_color='#3a7ca5', text_color='#ffffff').pack(padx = 10,pady = (10,5))

            popup_window_all_relative.after(100, lambda: popup_window_all_relative.focus_force())
            popup_window_all_relative.bind("<FocusOut>", lambda e: popup_window_all_relative.destroy())

        def edit_relative(relative_id):
            def get_data_relative():
                print(relative_id)
                relative_data = self.db.get_data_for_ralative_id(relative_id)
                id_data.configure(text=relative_data[0])
                title_data.set(relative_data[1])
                fname_data.insert(0,relative_data[2])
                lname_data.insert(0,relative_data[3])
                address_data.insert("1.0", relative_data[4])
                tel_data.insert(0,relative_data[5])
                
            def update_data_relative():
                data = []
                # data.append(title_data.get(),fname_data.get().strip(),lname_data.get().strip(),address_data.get("1.0", ctk.END).strip(),tel_data.get().strip())
                data.append(title_data.get())
                data.append(fname_data.get().strip())
                data.append(lname_data.get().strip())
                data.append(address_data.get('1.0',ctk.END).strip())
                data.append(tel_data.get().strip())
                print(data)
                print(relative_id)
                result = self.db.edit_relative(data,relative_id)
                if result:
                    messagebox.showinfo('แก้ไขข้อมูล',f'แก้ไขข้อมูลของ {data[1]} {data[2]} สำเร็จ')
                    for row in tree.get_children():
                        tree.delete(row)
                    start_tree()


            def on_close():
                print('ปิดแก้ไขข้อมูลญาติ')
                popup_edit_relative.destroy()

            popup_edit_relative = ctk.CTkToplevel(self)
            popup_edit_relative.title('แก้ไขข้อมูลญาติ')
            popup_edit_relative.geometry('480x720+1+1')
            popup_edit_relative.grab_set()
            popup_edit_relative.configure(fg_color='#f4f7fa')  # เพิ่มสีพื้นหลังให้สอดคล้องกับธีม

            relative_frame = ctk.CTkFrame(popup_edit_relative, fg_color='#ffffff', corner_radius=16)  # เพิ่มสีและมุมมน
            relative_frame.pack(fill='both',expand = True, padx=20, pady=20)  # เพิ่ม padding

            relative_frame.grid_columnconfigure((0,1),weight=1,uniform='move_adjust',minsize=100)
            relative_frame.grid_rowconfigure((0,1,2,3,4,5,6),weight=1,uniform='move_adjust')

            label_content = ctk.CTkLabel(relative_frame,text='แก้ไขข้อมูลญาติ',font=('TH SarabunPSK',40,'bold'))
            label_content.grid(row = 0,column = 0,columnspan = 2,sticky = 'nsew' , pady = 10)

            label_id = ctk.CTkLabel(relative_frame,text='รหัสประจำตัว : ',font=('TH SarabunPSK',18,'bold'))
            label_id.grid(row = 1,column = 0,sticky = 'e',padx = 5)
            label_title = ctk.CTkLabel(relative_frame,text='คำนำหน้า : ',font=('TH SarabunPSK',18,'bold'))
            label_title.grid(row = 2,column = 0,sticky = 'e',padx = 5)
            label_name = ctk.CTkLabel(relative_frame,text='ชื่อ : ',font=('TH SarabunPSK',18,'bold'))
            label_name.grid(row = 3,column = 0,sticky = 'e',padx = 5)
            label_lname = ctk.CTkLabel(relative_frame,text='นามสกุล : ',font=('TH SarabunPSK',18,'bold'))
            label_lname.grid(row = 4,column = 0,sticky = 'e',padx = 5)
            label_address = ctk.CTkLabel(relative_frame,text='ที่อยู่ : ',font=('TH SarabunPSK',18,'bold'))
            label_address.grid(row = 5,column = 0,sticky = 'e',padx = 5)
            label_tel = ctk.CTkLabel(relative_frame,text='เบอร์โทร : ',font=('TH SarabunPSK',18,'bold'))
            label_tel.grid(row = 6,column = 0,sticky = 'e',padx = 5)
        
            id_data = ctk.CTkLabel(relative_frame,text='',font=('TH SarabunPSK',18))
            title_data = ctk.CTkOptionMenu(relative_frame,values=['นาย','นาง','นางสาว','เด็กหญิง','เด็กชาย'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
            fname_data = ctk.CTkEntry(relative_frame,font=('TH SarabunPSK',18))
            lname_data = ctk.CTkEntry(relative_frame,font=('TH SarabunPSK',18))
            address_data = ctk.CTkTextbox(relative_frame,font=('TH SarabunPSK',18),height=60)
            tel_data = ctk.CTkEntry(relative_frame,font=('TH SarabunPSK',18))
           
            id_data.grid(row = 1,column = 1,sticky = 'w',padx = 5)
            title_data.grid(row = 2,column = 1,sticky = 'w',padx = 5)
            fname_data.grid(row = 3,column = 1,sticky = 'w',padx = 5)
            lname_data.grid(row = 4,column = 1,sticky = 'w',padx = 5)
            address_data.grid(row = 5,column = 1 ,sticky = 'w',padx = 5)
            tel_data.grid(row = 6,column = 1,sticky = 'w',padx = 5)

            button_submit = ctk.CTkButton(relative_frame,
                                                        text='บันทึกข้อมูล',
                                                        width=100,
                                                        font=('TH SarabunPSK',18,'bold'),
                                                        command=lambda:update_data_relative()
                                                        )
            button_submit.grid(row = 7,column = 0,columnspan = 2,sticky = 'n',padx = 5,pady = 10)
            get_data_relative()
            popup_edit_relative.protocol("WM_DELETE_WINDOW", on_close)

        def show_relative(relative_id,relative_name):
            def resize_tree_columns():
                tree_container_relative.update_idletasks()
                total_width = tree_container_relative.winfo_width()
                for col, ratio in column_ratio.items():
                    tree_relative.column(col,width=int(total_width * ratio),anchor='w')

            def on_close():
                print('ปิด show list')
                popup_show_list.destroy()

            popup_show_list = ctk.CTkToplevel()
            popup_show_list.title('รายชื่อญาติ')
            popup_show_list.geometry('720x480+1+1')
            popup_show_list.grab_set()
            popup_show_list.focus_set()
            ctk.CTkLabel(popup_show_list,text=f'ข้อมูลญาติของ {relative_name}',font=('TH SarabunPSK',40,'bold')).grid(row = 0,column = 0,sticky = 'nsew')

            tree_container_relative = ctk.CTkFrame(popup_show_list)
            tree_container_relative.grid(row = 2,column=0,padx=20, pady=10, sticky="nsew")

            tree_container_relative.grid_rowconfigure(1,weight=1)
            tree_container_relative.grid_columnconfigure(0,weight=1)
            popup_show_list.grid_rowconfigure(2, weight=1)
            popup_show_list.grid_columnconfigure(0, weight=1)

            tree_relative = ttk.Treeview(tree_container_relative,columns=('prisoner_id','f_name','l_name','level','dan','relation'),show='headings',height=10)
            tree_relative.heading('prisoner_id',text='รหัสประจำตัว')
            tree_relative.heading('f_name',text='ชื่อ')
            tree_relative.heading('l_name',text='นามสกุล')
            tree_relative.heading('level',text='ชั้น')
            tree_relative.heading('dan',text='แดน')
            tree_relative.heading('relation',text='ความสัมพันธ์')

            tree_relative.column('prisoner_id')
            tree_relative.column('f_name')
            tree_relative.column('l_name')
            tree_relative.column('level')
            tree_relative.column('dan')
            tree_relative.column('relation')

            scrollbar = ttk.Scrollbar(tree_container_relative,orient='vertical',command=tree.yview)
            tree_relative.configure(yscrollcommand=scrollbar.set)
            tree_relative.grid(row=1,column=0,sticky='nsew')
            scrollbar.grid(row=1,column=1,sticky='ns')

            column_ratio ={
                'prisoner_id' : 0.15,
                'f_name' : 0.20,
                'l_name' : 0.20,
                'level' : 0.15,
                'dan' : 0.15,
                'relation' : 0.15,
            }
            result = self.db.get_join_relatives_and_prisoners(relative_id)
            print(result)
            for row in result:
                tree_relative.insert('','end',values=row)

            tree_relative.bind('<Configure>',lambda e:resize_tree_columns())
            popup_show_list.protocol("WM_DELETE_WINDOW", on_close)

        # insert ข้อมูลให้อยู่ในตาราง treeview
        def show_relatives(data):
            for row in tree.get_children():
                tree.delete(row)
            
            # Check if data is valid and iterable
            if data and isinstance(data, (list, tuple)):
                for row in data:
                    tree.insert('','end',values=row)
            else:
                print("Warning: ข้อมูลญาติไม่ถูกต้องหรือเป็นค่าว่าง")

        # ค้นหาข้อมูลจากตาราง แค่คนเดียว 
        def search_one_var_prisoners():
            nonlocal all_data
            keyword = search_all_var.get().lower()
            filtered = [
                row for row in all_data 
                if keyword in row[2].lower() or keyword in row[3].lower()
            ]
            print(filtered)
            show_relatives(filtered)

        def resize_tree_columns():
            tree_container.update_idletasks()
            total_width = tree_container.winfo_width()
            for col, ratio in column_ratios.items():
                tree.column(col,width=int(total_width * ratio),anchor='w')

        def start_tree():
            nonlocal all_data
            data_result = self.db.get_all_relatives()
            if isinstance(data_result, list):
                all_data = data_result
                show_relatives(all_data)
            else:
                print("Error: ไม่สามารถโหลดข้อมูลญาติได้")
                all_data = []
                show_relatives(all_data)

        self.show_all_relative_frame.grid_rowconfigure(2,weight=1)
        self.show_all_relative_frame.grid_columnconfigure(0,weight=1)

        search_all_var = tk.StringVar()
        
        # หัวข้อ
        ctk.CTkLabel(self.show_all_relative_frame,text='รายชื่อญาติทั้งหมด',font=('TH SarabunPSK',40,'bold')).grid(row = 0,column = 0,pady = 10,sticky = 'n')

        # ช่องค้นหา
        search_entry = ctk.CTkEntry(self.show_all_relative_frame,placeholder_text='พิมพ์ชื่อเพื่อค้นหา...',font=('TH SarabunPSK',18),width=200,textvariable=search_all_var)
        search_entry.grid(row = 1,column = 0, pady = 10,sticky = 'n')
        search_all_var.trace_add("write",lambda *args:search_one_var_prisoners())

        tree_container = ctk.CTkFrame(self.show_all_relative_frame)
        tree_container.grid(row = 2,column=0,padx=20, pady=10, sticky="nsew")

        tree_container.grid_rowconfigure(0,weight=1)
        tree_container.grid_columnconfigure(0,weight=1)

        # กำหนด style สำหรับ treeview 
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Treeview',font =('TH SarabunPSK',16),rowheight = 35)
        style.configure('Treeview.Heading',font = ('TH SarabunPSK',16,'bold'))

        tree = ttk.Treeview(tree_container,columns=('relative_id','title','f_name','l_name','address','tel'),show='headings',height=10)
        tree.heading('relative_id',text='หมายเลขบัตรประชาชน')
        tree.heading('title',text='คำนำหน้า')
        tree.heading('f_name',text='ชื่อ')
        tree.heading('l_name',text='นามสกุล')
        tree.heading('address',text='ที่อยู่')
        tree.heading('tel',text='เบอร์โทร')

        tree.column('relative_id')
        tree.column('title')
        tree.column('f_name')
        tree.column('l_name')
        tree.column('address')
        tree.column('tel')

        scrollbar = ttk.Scrollbar(tree_container,orient='vertical',command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.grid(row=0,column=0,sticky='nsew')
        scrollbar.grid(row=0,column=1,sticky='ns')

        all_data = []

        column_ratios = {
            'relative_id' : 0.14,
            'title' : 0.08,
            'f_name' : 0.19,
            'l_name' : 0.19,
            'address' : 0.28,
            'tel' : 0.12,
        }

        start_tree()
        tree.bind('<Configure>',lambda e:resize_tree_columns())
        tree.bind('<Button-3>',on_right_click)
        popup_window_all_relative = None

##############################################################################################################################################################################
    # ลงทะเบียนลายนิ้วมือ
##############################################################################################################################################################################
    def register_fingerprint(self):
        def show_regis_data():
            show_regis_data_search.grid(row = 2,column = 0,columnspan = 2,sticky = 'nsew')
            
            for i in range(2):
                show_regis_data_search.grid_columnconfigure(i,weight=1,uniform='show_regis')
            for i in range(7):
                show_regis_data_search.grid_rowconfigure(i,weight=1,uniform='show_regis')

            label_national_id = ctk.CTkLabel(show_regis_data_search,text='รหัสประจำตัว : ',font=('TH SarabunPSK',18,'bold'),text_color='#4a4a4a')
            label_national_id.grid(row = 0,column = 0,padx = 5,sticky = 'e')

            entry_national_id = ctk.CTkEntry(show_regis_data_search,textvariable=show_regis_id_var,state = 'disabled',font=('TH SarabunPSK',18),
                fg_color='#f8f9fa', text_color='#2d3a4b', border_color='#e3eefa', border_width=2)
            entry_national_id.grid(row = 0,column = 1,padx = 5,sticky = 'w')

            label_title = ctk.CTkLabel(show_regis_data_search,text='คำนำหน้า : ',font=('TH SarabunPSK',18,'bold'),text_color='#4a4a4a')
            label_title.grid(row = 1,column = 0,sticky = 'e',padx = 5)

            combo_title = ctk.CTkOptionMenu(show_regis_data_search,values=['นาย','นาง','นางสาว','เด็กหญิง','เด็กชาย'],variable=show_regis_title,font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18),
                fg_color='#ffffff', button_color='#4f8cff', text_color='#222')
            combo_title.grid(row = 1,column = 1,sticky = 'w',padx = 5)

            label_f_name = ctk.CTkLabel(show_regis_data_search,text='ชื่อ : ',font=('TH SarabunPSK',18,'bold'),text_color='#4a4a4a')
            label_f_name.grid(row = 2,column = 0,padx= 5,sticky = 'e')

            entry_f_name = ctk.CTkEntry(show_regis_data_search,font=('TH SarabunPSK',18),textvariable=show_regis_entry_fname_var,
                fg_color='#ffffff', text_color='#2d3a4b', border_color='#4f8cff', border_width=2)
            entry_f_name.grid(row = 2,column = 1,padx= 5,sticky = 'w')

            label_l_name = ctk.CTkLabel(show_regis_data_search,text='นามสกุล : ',font=('TH SarabunPSK',18,'bold'),text_color='#4a4a4a')
            label_l_name.grid(row = 3,column = 0,padx= 5,sticky = 'e')

            entry_l_name = ctk.CTkEntry(show_regis_data_search,font=('TH SarabunPSK',18),textvariable=show_regis_entry_lname_var,
                fg_color='#ffffff', text_color='#2d3a4b', border_color='#4f8cff', border_width=2)
            entry_l_name.grid(row = 3,column = 1,padx= 5,sticky = 'w')

            label_address = ctk.CTkLabel(show_regis_data_search,text='ที่อยู่ : ',font=('TH SarabunPSK',18,'bold'),text_color='#4a4a4a')
            label_address.grid(row = 4,column = 0,padx= 5,sticky = 'e')

            entry_address = ctk.CTkEntry(show_regis_data_search,font=('TH SarabunPSK',18),textvariable=show_regis_entry_address_var,
                fg_color='#ffffff', text_color='#2d3a4b', border_color='#4f8cff', border_width=2)
            entry_address.grid(row = 4,column = 1,padx= 5,sticky = 'w')

            label_tel = ctk.CTkLabel(show_regis_data_search,text='เบอร์โทร : ',font=('TH SarabunPSK',18,'bold'),text_color='#4a4a4a')
            label_tel.grid(row = 5,column = 0,padx= 5,sticky = 'e')

            entry_tel = ctk.CTkEntry(show_regis_data_search,font=('TH SarabunPSK',18),textvariable=show_regis_entry_tel_var,
                fg_color='#ffffff', text_color='#2d3a4b', border_color='#4f8cff', border_width=2)
            entry_tel.grid(row = 5,column = 1,padx= 5,sticky = 'w')

            label_fingerprint = ctk.CTkLabel(show_regis_data_search,text='ลายนิ้วมือ : ',font=('TH SarabunPSK',18,'bold'),text_color='#4a4a4a')
            label_fingerprint.grid(row = 6 ,column = 0,padx = 5,sticky = 'e')

            label_fingerprint_state.grid(row = 6 ,column = 1,padx = 5,sticky = 'w')

            # ctk.CTkLabel(show_regis_data_search,text='label',fg_color='red').pack(expand=True,fill='both')
            ctk.CTkButton(show_regis_data_search,
                          text='ลงทะเบียน',
                          font=('TH SarabunPSK',18,'bold'),
                          command=lambda:insert_fingerprint_to_db()
                          ).grid(row = 7,column = 0,pady = 10,sticky = 'e',padx = 5)
            
            ctk.CTkButton(show_regis_data_search,
                          text='เสร็จสิ้น',
                          font=('TH SarabunPSK',18,'bold'),
                          command=lambda:destroy_frame_show_regis()
                          ).grid(row = 7,column = 1,pady = 10,sticky = 'w',padx = 5)

        def destroy_frame_show_regis():
            regis_fp_entry.delete(0,tk.END)
            for widgets in show_regis_data_search.winfo_children():
                widgets.grid_forget()

        def get_data_relative():
            def read_card():
                try:
                    self.thai_id_reader.read_card()
                    info = self.thai_id_reader.get_person_info()
                except Exception as e:
                    print(f'เกิดข้อผิดพลาดในการอ่านบัตรประชาชน : {e}')
                    messagebox.showerror('Error การอ่านบัตรประชาชน','กรุณาตรวจสอบการเชื่อมต่อเครื่องอ่านบัตรประชาชน และเสียบบัตรประชาชน')
                    return
                return info['cid']
            
            if read_card():
                regis_fp_entry.delete(0,tk.END)
                regis_fp_entry.insert(0,read_card())
                n_id = str(regis_fp_entry.get())
                get_data(n_id)

            else:
                print('ไม่พบบัตร')
                return

        def get_data_manual():
            n_id = str(regis_fp_entry.get())
            get_data(n_id)

        def get_data(n_id):
            result = self.db.get_data_for_ralative_id(n_id)
            if result:
                print(result[0])
                show_regis_id_var.set(result[0])
                show_regis_title.set(result[1])
                show_regis_entry_fname_var.set(result[2])
                show_regis_entry_lname_var.set(result[3])
                show_regis_entry_address_var.set(result[4])
                show_regis_entry_tel_var.set(result[5])
                if result[6] == None:
                    label_fingerprint_state.configure(text = f'{emoji.emojize(':cross_mark: ไม่พบลายนิ้วมือ')}',text_color='#FE0000')
                else:
                    label_fingerprint_state.configure(text = f'{emoji.emojize(':check_mark: ลงทะเบียนเรียบร้อย')}',text_color='#00CC00')
                show_regis_data()
            else:
                messagebox.showerror('แจ้งเตือน',f'ไม่พบข้อมูลหมายเลขประจำตัว {regis_fp_entry.get()}')

        def insert_fingerprint_to_db():
            popup_fingerprint = ctk.CTkToplevel(popup_register_fingerprint)
            popup_fingerprint.transient(popup_register_fingerprint)
            popup_fingerprint.title('เก็บลายนิ้วมือ')
            popup_fingerprint.geometry('300x300+450+200')
            popup_fingerprint.grab_set()
            popup_fingerprint.focus_set()
            popup_fingerprint.configure(fg_color='#f4f7fa')  # เพิ่มสีพื้นหลังให้สอดคล้องกับธีม
                        # เพิ่มการตรวจสอบว่าเธรดกำลังทำงานหรือไม่
            is_thread_running = False

            label_on_popup_fingerprint = ctk.CTkLabel(popup_fingerprint,text='',font=('TH SarabunPSK',32,'bold'))
            label_on_popup_fingerprint.pack(expand = True,fill = 'both')
            progressbar = ctk.CTkProgressBar(popup_fingerprint,
                                             width= 280,
                                             mode='indeterminate')
            progressbar.stop()

            button_submit = ctk.CTkButton(popup_fingerprint,
                                   text='บันทึกลายนิ้วมือ',
                                   font=('TH SarabunPSK',18,'bold'),
                                   command=lambda:start_capture())
            button_submit.pack(side='left',pady = 5)
            button_cancel = ctk.CTkButton(popup_fingerprint,
                                   text='ยกเลิก',
                                   font=('TH SarabunPSK',18,'bold'),
                                   command=lambda:popup_fingerprint.destroy())
            button_cancel.pack(side='right',pady = 5)

            def start_capture():
                try:
                    self.zkfp2.Init()
                    self.zkfp2.OpenDevice(0)
                except Exception as e:
                    messagebox.showerror('การเชื่อมต่อเครื่อง','กรุณาเชื่อมต่อเครื่องสแกนนิ้ว')
                    return
                nonlocal is_thread_running

                if is_thread_running:
                    messagebox.showwarning('คำเตือน', 'โปรแกรมกำลังจับลายนิ้วมืออยู่ โปรดลองอีกครั้ง')
                    return

                is_thread_running = True
                button_submit.pack_forget()
                button_cancel.pack_forget()
                progressbar.pack(padx=10, pady=10)
                progressbar.start()
                
                def run():
                    try:
                        label_on_popup_fingerprint.configure(text='เครื่องสแกนพร้อม\nกรุณาวางนิ้วมือบนเครื่อง')
                        template = []

                        for i in range(3):
                            while True:
                                capture = self.zkfp2.AcquireFingerprint()
                                if capture:
                                    tmp, img = capture
                                    template.append(tmp)

                                    label_on_popup_fingerprint.after(0, lambda i=i: label_on_popup_fingerprint.configure(
                                        text=f"{i + 1}", font=('TH SarabunPSK', 56, 'bold')
                                    ))

                                    break

                        regTemp, regTempLen = self.zkfp2.DBMerge(*template)
                        if regTemp:
                            label_on_popup_fingerprint.configure(text='กำลังบันทึกข้อมูล\nกรุณารอสักครู่')
                            result = self.db.set_fingerprint(show_regis_id_var.get(), bytes(regTemp))

                            if result:
                                on_success()
                            else:
                                messagebox.showerror('ผิดพลาด', 'ไม่สามารถบันทึกข้อมูลลายนิ้วมือได้')
                                return
                    except Exception as e:
                        messagebox.showerror('ผิดพลาด', f'เกิดข้อผิดพลาด: {e}')
                    finally:
                        is_thread_running = False

                def on_success():
                    label_on_popup_fingerprint.configure(text='บันทึกเสร็จสิ้น')
                    popup_fingerprint.after(1000, lambda: popup_fingerprint.destroy())
                    self.zkfp2.CloseDevice()
                    print(f'id = {show_regis_id_var.get()}')
                    get_data(show_regis_id_var.get())
                    # insert_fingerprint_to_db()

                threading.Thread(target=run, daemon=True).start()
            
        def on_close():
            print('ปิดหน้าต่าง popup_register_fingerprint')
            popup_register_fingerprint.destroy()

        popup_register_fingerprint = ctk.CTkToplevel(self)
        popup_register_fingerprint.title('ลงทะเบียนลายนิ้วมือ')
        popup_register_fingerprint.geometry('480x720+1+1')
        popup_register_fingerprint.grab_set()
        popup_register_fingerprint.configure(fg_color='#f4f7fa')  # เพิ่มสีพื้นหลังให้สอดคล้องกับธีม

        popup_register_fingerprint.grid_rowconfigure(2,weight=1,uniform='regis_fg')
        popup_register_fingerprint.grid_columnconfigure((0,1),weight=1,uniform='regis_fg')


        show_regis_id_var = ctk.StringVar()
        show_regis_title = ctk.StringVar()
        show_regis_entry_fname_var = ctk.StringVar()
        show_regis_entry_lname_var = ctk.StringVar()
        show_regis_entry_address_var = ctk.StringVar()
        show_regis_entry_tel_var = ctk.StringVar()

        ctk.CTkLabel(popup_register_fingerprint,text='ลงทะเบียนลายนิ้วมือ',font=('TH SarabunPSK',28,'bold'),text_color='#2d3a4b').grid(row = 0,column = 0,columnspan = 2,sticky = 'nsew',pady = 30)

        regis_fp_entry = ctk.CTkEntry(popup_register_fingerprint,width=150,font=('TH SarabunPSK',18),validate='key',validatecommand = (self.vcmd,'%P'),
            fg_color='#ffffff', text_color='#2d3a4b', border_color='#4f8cff', border_width=2)
        regis_fp_entry.grid(row = 1,column = 0,sticky = 'e',padx = 5,pady = 10)

        regis_fp_search_bt = ctk.CTkButton(popup_register_fingerprint,
                                                text='ค้นหาด้วยบัตรประชาชน',
                                                width=150,
                                                font=('TH SarabunPSK',18,'bold'),
                                                fg_color='#4f8cff', hover_color='#2d3a4b', text_color='#ffffff',
                                                command=lambda:get_data_relative())
        regis_fp_search_bt.grid(row=1,column = 1,sticky = 'w',padx = 5,pady = 10)
        show_regis_data_search = ctk.CTkFrame(popup_register_fingerprint, fg_color='#ffffff', corner_radius=16, border_width=2, border_color='#e3eefa')
        label_fingerprint_state = ctk.CTkLabel(show_regis_data_search,font=('TH SarabunPSK',18,'bold'),text='',text_color='#2d3a4b')

        days = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์","อาทิตย์"]
        months = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน",
                    "พฤษภาคม","มิถุนายน","กรกฎาคม", "สิงหาคม",
                    "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]

        current_time = t.localtime()
        day = days[current_time.tm_wday]
        month = months[current_time.tm_mon - 1]
        regis_fp_entry.bind('<Return>',lambda event:get_data_manual())

        popup_register_fingerprint.protocol("WM_DELETE_WINDOW", on_close)
##############################################################################################################################################################################
    # รายการจองเยี่ยม
##############################################################################################################################################################################
    def reserve_to_visit(self):
        # เคลียร์วิดเจ็ตที่ถูกสร้างแบบไดนามิก
        def clear_dynamic_widgets():
            try:
                # ซ่อนทุกวิดเจ็ตใน main_frame ยกเว้นปุ่มเริ่มต้น
                for w in main_frame.grid_slaves():
                    if w not in (button_visitor,):
                        try:
                            w.grid_forget()
                        except Exception:
                            pass
            except Exception:
                pass
            try:
                # ซ่อน frame ที่ถูกวางไว้บน popup โดยตรง (เช่น reserve_header_frame)
                for w in popup_reserve_to_visit.grid_slaves():
                    if w not in (top_frame, main_frame):
                        try:
                            w.grid_forget()
                        except Exception:
                            pass
            except Exception:
                pass
            try:
                main_frame_label.configure(text='')
            except Exception:
                pass

        # เลิก bind อีเวนต์ที่ผูกไว้สำหรับ idle timer
        def unbind_idle_events():
            for seq in ("<Any-KeyPress>", "<Button>", "<Motion>", "<MouseWheel>"):
                try:
                    popup_reserve_to_visit.unbind_all(seq)
                except Exception:
                    pass

        def config_label():
            nonlocal nationnal_id, idle_bind_set
            cancel_idle_timer() # ยกเลิก timer ทุกครั้งที่กลับหน้าหลัก
            # เคลียร์วิดเจ็ต/เฟรมที่แสดงอยู่
            clear_dynamic_widgets()
            # เลิก bind อีเวนต์ (ถ้ามี)
            if idle_bind_set:
                unbind_idle_events()
                idle_bind_set = False
            nationnal_id = None
            hide_progress()
            date_label.pack(fill='both', expand=True)
            main_frame_label.grid_forget()
            button_reserve_now.grid_forget()
            button_reserve_future.grid_forget()
            button_cancel.grid_forget()
            button_visitor.grid(row=0,rowspan = 3 , column=0, columnspan=2, sticky='ew', padx=20, pady=20)

            update_time_label()

        # ----- Idle timer helpers (30s) -----
        idle_after_id = None
        idle_bind_set = False

        def cancel_idle_timer():
            nonlocal idle_after_id
            if idle_after_id:
                try:
                    popup_reserve_to_visit.after_cancel(idle_after_id)
                except Exception:
                    pass
                idle_after_id = None    

        def on_idle_timeout():
            cancel_idle_timer()
            if popup_reserve_to_visit.winfo_exists():
                # เคลียร์วิดเจ็ตเมื่อไม่มีการใช้งาน
                clear_dynamic_widgets()
                config_label()

        def reset_idle_timer():
            nonlocal idle_after_id
            cancel_idle_timer()
            idle_after_id = popup_reserve_to_visit.after(30000,on_idle_timeout)

        def get_relative():
            nonlocal idle_bind_set
            reset_idle_timer()
            if not idle_bind_set:
                # รีเซ็ต timer เมื่อมีการกระทำของผู้ใช้
                for seq in ("<Any-KeyPress>", "<Button>", "<Motion>", "<MouseWheel>"):
                    popup_reserve_to_visit.bind_all(seq, lambda e: reset_idle_timer(), add="+")
                idle_bind_set = True

            now = datetime.now().time()
            # ลบปุ่มเดิมถ้ามี
            for widget in main_frame.grid_slaves():
                if isinstance(widget, ctk.CTkButton) and widget != button_visitor:
                    widget.grid_forget()

            if not nationnal_id:
                messagebox.showwarning('แจ้งเตือน', 'ไม่พบเลขบัตรประชาชน')
                main_frame_label.configure(text='ไม่พบเลขบัตรประชาชน')
                return
            prisoners_data = self.db.get_join_relatives_and_prisoners(nationnal_id)
            relative_data = self.db.get_data_for_ralative_id(nationnal_id)
            if not relative_data:
                main_frame_label.configure(text='ไม่พบข้อมูลญาติ')
                messagebox.showwarning('แจ้งเตือน', 'ไม่พบข้อมูลญาติในระบบ')
                return
            relative_name = f'{relative_data[1]}{relative_data[2]} {relative_data[3]}'
            main_frame_label.configure(text=f'ยินดีต้อนรับ\n{relative_name}')

            button_reserve_now.configure(
                text='จองเยี่ยมวันนี้',
                font=('TH SarabunPSK', 64, 'bold'),
                fg_color='#4f8cff',
                hover_color='#2d3a4b',
                text_color='#fff',
                corner_radius=12,
                command=lambda: (cancel_idle_timer(), reserve_now(), button_reserve_now.grid_forget(), button_reserve_future.grid_forget(), button_cancel.grid_forget()),
                height=48,
                width=220
            )
            button_reserve_future.configure(
                text='จองเยี่ยมล่วงหน้า',
                font=('TH SarabunPSK', 64, 'bold'),
                fg_color="#60bedb",
                hover_color='#b3d1ff',
                text_color='#2d3a4b',
                corner_radius=12,
                command=lambda: (cancel_idle_timer(), reserve_future()),
                height=48,
                width=220
            )
            button_cancel.configure(
                fg_color='red',
                text='ยกเลิก',
                font=('TH SarabunPSK', 64, 'bold'),
                text_color='#fff',
                corner_radius=12,
                command=lambda: (cancel_idle_timer(), config_label()),
                height = 30,
                width = 120
            )
            button_reserve_now.grid(row=1, column=0, sticky='nsew', padx=20, pady=5)
            button_reserve_future.grid(row=1, column=1, sticky='nsew', padx=20, pady=5)
            button_cancel.grid(row=2, column=0, columnspan=2,sticky='nsew', padx=200, pady=100)

            def reserve_now():
                cancel_idle_timer()
                button_reserve_now.grid_forget()
                button_reserve_future.grid_forget()
                button_cancel.grid_forget()

                def reserve_visit(prisoner_data):
                    today_now = datetime.today().date().isoformat()
                    month_now = today_now[:7]
                    reserve = RESERVE(
                        main_window=popup_reserve_to_visit, 
                        prisoner_data=prisoner_data,
                        national_id=nationnal_id,
                        to_day=today_now,
                        to_month=month_now,
                        reserve_now=True
                    )
            
                    # ปิดอัตโนมัติถ้าไม่มีการใช้งาน 20 วินาที
                    idle_after_id = {"id": None}

                    def cancel_idle():
                        if idle_after_id["id"]:
                            try:
                                reserve.next_screen.after_cancel(idle_after_id["id"])
                            except Exception:
                                pass
                            idle_after_id["id"] = None

                    def on_idle_timeout():
                        cancel_idle()
                        try:
                            reserve.on_close()
                        except Exception:
                            pass

                    def reset_idle(_=None):
                        cancel_idle()
                        try:
                            if reserve.next_screen and reserve.next_screen.winfo_exists():
                                idle_after_id["id"] = reserve.next_screen.after(20000, on_idle_timeout)
                        except Exception:
                            pass

                    # เริ่มนับเวลาและผูกอีเวนต์เพื่อรีเซ็ตเวลา
                    reset_idle()
                    for seq in ("<Any-KeyPress>", "<Button>", "<Motion>", "<MouseWheel>"):
                        try:
                            reserve.next_screen.bind_all(seq, reset_idle, add="+")
                        except Exception:
                            pass

                    # เคลียร์ binding และตัวจับเวลาเมื่อหน้าต่างถูกปิด
                    def _cleanup(_e=None):
                        try:
                            for seq in ("<Any-KeyPress>", "<Button>", "<Motion>", "<MouseWheel>"):
                                reserve.next_screen.unbind_all(seq)
                        except Exception:
                            pass
                        cancel_idle()

                    try:
                        reserve.next_screen.bind("<Destroy>", _cleanup, add="+")
                    except Exception:
                        pass

                def item_select(_):
                    try:
                        cancel_idle_timer()
                        for i in tree.selection():
                            prisoner_data = tree.item(i)['values']
                            break
                        if self.open_nextscreen_window is None or not self.open_nextscreen_window.winfo_exists():
                            self.open_nextscreen_window = reserve_visit(prisoner_data)
                        else:
                            self.open_nextscreen_window.lift()
                    except Exception as e:
                        print(f'เกิดข้อผิดพลาด item_select(_) : {e}')

                def resize_tree_column():
                    tree_container.update_idletasks()
                    total_width = tree_container.winfo_width()
                    for col, ratio in column_ratios.items():
                        tree.column(col,width=int(total_width * ratio),anchor='w')

                # Add a beautiful frame for the treeview
                tree_container = ctk.CTkFrame(
                    main_frame,
                    fg_color="#f8fbff",
                    corner_radius=18,
                    border_width=2,
                    border_color="#3a7ca5"
                )
                tree_container.grid_rowconfigure(1,weight=1)
                tree_container.grid_columnconfigure(0,weight=1)

                # กำหนด style สำหรับ treeview 
                style = ttk.Style()
                style.theme_use('clam')
                style.configure('Treeview',
                    font =('TH SarabunPSK', 20),
                    rowheight = 38,
                    background="#f8fbff",
                    fieldbackground="#f8fbff",
                    bordercolor="#3a7ca5",
                    borderwidth=1
                )
                style.configure('Treeview.Heading',
                    font = ('TH SarabunPSK', 22, 'bold'),
                    background="#3a7ca5",
                    foreground="#ffffff",
                    borderwidth=2
                )
                style.map('Treeview', background=[('selected', '#b3d1ff')])

                tree = ttk.Treeview(
                    tree_container,
                    columns=('prisoner_id','f_name','l_name','level','dan','relation'),
                    show='headings',
                    height=10,
                    style='Treeview'
                )
                tree.heading('prisoner_id',text='รหัสประจำตัว')
                tree.heading('f_name',text='ชื่อ')
                tree.heading('l_name',text='นามสกุล')
                tree.heading('level',text='ชั้น')
                tree.heading('dan',text='แดน')
                tree.heading('relation',text='ความสัมพันธ์')
                tree.column('prisoner_id', anchor='center')
                tree.column('f_name', anchor='center')
                tree.column('l_name', anchor='center')
                tree.column('level', anchor='center')
                tree.column('dan', anchor='center')
                tree.column('relation', anchor='center')
                scrollbar = ttk.Scrollbar(tree_container,orient='vertical',command=tree.yview)
                tree.configure(yscrollcommand=scrollbar.set)

                
                btn_cancel = ctk.CTkButton(
                    main_frame,
                    text='ย้อนกลับ',
                    font=('TH SarabunPSK', 52, 'bold'),
                    fg_color="#eec337",
                    hover_color="#dad099",
                    text_color="#000000",
                    corner_radius=16,
                    command=lambda: (
                        tree_container.grid_forget(),
                        btn_cancel.grid_forget(),
                        get_relative()
                    )
                )
                btn_cancel.grid(
                    row=2,
                    column=0,
                    columnspan=2,
                    sticky='nsew',
                    padx=200,
                    pady=100
                    )
                
                column_ratios = {
                    'prisoner_id': 0.15,
                    'f_name': 0.18,
                    'l_name': 0.18,
                    'level': 0.15,
                    'dan': 0.17,
                    'relation': 0.17,
                }

                print('จองเยี่ยมวันนี้')
                allowed_dan_by_dan = {
                    "จันทร์" : ['6','รจช'],
                    "อังคาร" : ['5','รจช'],
                    "พุธ" : ['1','2','3','4','7','รจช'],
                    "พฤหัสบดี" : ['5','6','รจช'],
                    "ศุกร์" : ['1','2','3','4','7','รจช']        
                }
                allower_dan = allowed_dan_by_dan.get(day,[])
                print(allower_dan)

                if prisoners_data != []:
                    print(prisoners_data)
                else:
                    alert = ALERT(popup_reserve_to_visit,[f'ไม่พบข้อมูล \n {nationnal_id}'],button=True)
                    
                    return
                for row in tree.get_children():
                    tree.delete(row)
                for index,row in enumerate(prisoners_data):
                    if row[4] not in allower_dan or row[6] != 'อยู่':
                        continue
                    tree.insert('','end',values=row)

                if len(tree.get_children()) == 0:
                    alert = ALERT(popup_reserve_to_visit,['ไม่พบข้อมูลผู้ต้องขังที่เยี่ยมได้\nกรุณาตรวจสอบวันและเวลาเยี่ยม'],button=False)
                    alert.after(3000,lambda: (alert.destroy()))
                else:
                    tree.grid(row=1,column=0,columnspan=2,sticky='nsew')
                    tree_container.grid(row = 1,column=0,columnspan = 2,padx=20, pady=10, sticky="nsew")

                tree_container.bind('<Configure>',lambda e: resize_tree_column())
                tree.bind('<<TreeviewSelect>>',item_select)

            def reserve_future():
                cancel_idle_timer()
                # main_frame.rowconfigure((1),weight=0,uniform='main_frame')
                # main_frame.rowconfigure((3),weight=1,uniform='main_frame')
                button_reserve_now.grid_forget()
                button_reserve_future.grid_forget()
                button_cancel.grid_forget()
                name_next_day = days[current_time.tm_wday+1]

                def reserve_visit(prisoner_data):
                    cal_next_day = CALCULATE_NEXT_DAY()
                    today_future = cal_next_day.get_next_day()
                    month_future = today_future[:7]
                    print(f'จองเยี่ยมล่วงหน้า {today_future} {month_future}')

                    reserve = RESERVE(
                        main_window=popup_reserve_to_visit,
                        prisoner_data=prisoner_data,
                        national_id=nationnal_id,
                        to_day=today_future,
                        to_month=month_future,
                        reserve_now=False
                    )
                    # ปิดอัตโนมัติถ้าไม่มีการใช้งาน 20 วินาที
                    idle_after_id = {"id": None}

                    def cancel_idle():
                        if idle_after_id["id"]:
                            try:
                                reserve.next_screen.after_cancel(idle_after_id["id"])
                            except Exception:
                                pass
                            idle_after_id["id"] = None

                    def on_idle_timeout():
                        cancel_idle()
                        try:
                            reserve.on_close()
                        except Exception:
                            pass

                    def reset_idle(_=None):
                        cancel_idle()
                        try:
                            if reserve.next_screen and reserve.next_screen.winfo_exists():
                                idle_after_id["id"] = reserve.next_screen.after(20000, on_idle_timeout)
                        except Exception:
                            pass

                    # เริ่มนับเวลาและผูกอีเวนต์เพื่อรีเซ็ตเวลา
                    reset_idle()
                    for seq in ("<Any-KeyPress>", "<Button>", "<Motion>", "<MouseWheel>"):
                        try:
                            reserve.next_screen.bind_all(seq, reset_idle, add="+")
                        except Exception:
                            pass

                    # เคลียร์ binding และตัวจับเวลาเมื่อหน้าต่างถูกปิด
                    def _cleanup(_e=None):
                        try:
                            for seq in ("<Any-KeyPress>", "<Button>", "<Motion>", "<MouseWheel>"):
                                reserve.next_screen.unbind_all(seq)
                        except Exception:
                            pass
                        cancel_idle()

                    try:
                        reserve.next_screen.bind("<Destroy>", _cleanup, add="+")
                    except Exception:
                        pass

                def item_select(_):
                    cancel_idle_timer()
                    print('item_select() called')
                    try:
                        for i in future_tree.selection():
                            prisoner_data = future_tree.item(i)['values']
                            break
                        if self.open_nextscreen_window is None or not self.open_nextscreen_window.winfo_exists():
                            self.open_nextscreen_window = reserve_visit(prisoner_data)
                        else:
                            self.open_nextscreen_window.lift()
                    except Exception as e:
                        print(f'เกิดข้อผิดพลาด item_select() : {e}')


                def resize_tree_column():
                    future_tree_container.update_idletasks()
                    total_width = future_tree_container.winfo_width()
                    for col, ratio in column_ratios.items():
                        future_tree.column(col,width=int(total_width * ratio),anchor='w')
               

                # Ensure previous widgets are hidden to avoid overlap
                for widget in popup_reserve_to_visit.grid_slaves():
                    if isinstance(widget, ctk.CTkLabel) and widget.cget("text").startswith("จองเยี่ยมล่วงหน้า"):
                        widget.grid_forget()

                
                cal_next_day = CALCULATE_NEXT_DAY()
                next_day = cal_next_day.get_next_day()
                dt = datetime.strptime(next_day, '%Y-%m-%d')
                # แปลงวันที่เป็น วัน เดือน ปี (พ.ศ.) ภาษาไทย
                thai_days = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
                thai_months = [
                    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
                    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
                ]
                weekday = thai_days[dt.weekday()]
                month = thai_months[dt.month - 1]
                year_th = dt.year + 543
                date_thai = f"วัน{weekday} ที่ {dt.day} {month} {year_th}"

                old_text = main_frame_label.cget('text')
                main_frame_label.configure(text = f'{old_text}\nจองเยี่ยมล่วงหน้าสำหรับ {date_thai}')
                
                # Add a beautiful frame for the treeview
                future_tree_container = ctk.CTkFrame(
                    main_frame,
                    fg_color="#f8fbff",
                    # corner_radius=18,
                    # border_width=2,
                    # border_color="#3a7ca5"
                )
                future_tree_container.grid_rowconfigure(1,weight=1)
                future_tree_container.grid_columnconfigure(0,weight=1)

                # กำหนด style สำหรับ treeview 
                style = ttk.Style()
                style.theme_use('clam')
                style.configure('Treeview',
                    font =('TH SarabunPSK', 20),
                    rowheight = 38,
                    background="#f8fbff",
                    fieldbackground="#f8fbff",
                    bordercolor="#3a7ca5",
                    borderwidth=1
                )
                style.configure('Treeview.Heading',
                    font = ('TH SarabunPSK', 22, 'bold'),
                    background="#3a7ca5",
                    foreground="#ffffff",
                    borderwidth=2
                )
                style.map('Treeview', background=[('selected', '#b3d1ff')])

                future_tree = ttk.Treeview(
                    future_tree_container,
                    columns=('prisoner_id','f_name','l_name','level','dan','relation'),
                    show='headings',
                    height=10,
                    style='Treeview'
                )
                future_tree.heading('prisoner_id',text='รหัสประจำตัว')
                future_tree.heading('f_name',text='ชื่อ')
                future_tree.heading('l_name',text='นามสกุล')
                future_tree.heading('level',text='ชั้น')
                future_tree.heading('dan',text='แดน')
                future_tree.heading('relation',text='ความสัมพันธ์')
                future_tree.column('prisoner_id', anchor='center')
                future_tree.column('f_name', anchor='center')
                future_tree.column('l_name', anchor='center')
                future_tree.column('level', anchor='center')
                future_tree.column('dan', anchor='center')
                future_tree.column('relation', anchor='center')
                scrollbar = ttk.Scrollbar(future_tree_container,orient='vertical',command=future_tree.yview)
                future_tree.configure(yscrollcommand=scrollbar.set)
                scrollbar.grid(row=0,column=1,sticky='ns',padx=(0, 4), pady=4)

                btn_cancel = ctk.CTkButton(
                    main_frame,
                    text='ย้อนกลับ',
                    font=('TH SarabunPSK', 32, 'bold'),
                    fg_color="#eec337",
                    hover_color="#dad099",
                    text_color="#000000",
                    corner_radius=16,
                    command=lambda: (

                        future_tree_container.grid_forget(),
                        btn_cancel.grid_forget(),
                        get_relative()
                    )
                )
                btn_cancel.grid(
                    row=2,
                    column=0,
                    columnspan=2,
                    sticky='nsew',
                    padx=200,
                    pady=100
                    )
                # ดึงข้อมูลผู้ต้องขังที่สามารถจองล่วงหน้าได้ (ตัวอย่าง: ใช้ prisoners_data เดิม)

                # กำหนดความกว้าง column
                column_ratios = {
                    'prisoner_id': 0.15,
                    'f_name': 0.18,
                    'l_name': 0.18,
                    'level': 0.15,
                    'dan': 0.17,
                    'relation': 0.17,
                }
                allowed_dan_by_dan={
                    "เสาร์" : [],
                    "จันทร์" : ['6','รจช'],
                    "อังคาร" : ['5','รจช'],
                    "พุธ" : ['1','2','3','4','7','รจช'],
                    "พฤหัสบดี" : ['5','6','รจช'],
                    "ศุกร์" : ['1','2','3','4','7','รจช'],
                    "เสาร์" : []
                }
                # print(days)
                try:
                    allowed_dan = allowed_dan_by_dan.get(weekday)
                except Exception as e:
                    print(f'เกิดข้อผิดพลาด {e}')
                
                if prisoners_data != []:
                    print(prisoners_data)
                    # ถ้าไม่มีข้อมูลผู้ต้องขังที่สามารถจองล่วงหน้าได้
                    # future_tree.insert('', 'end', values=('ไม่มีข้อมูล', '', '', '', '', ''))
                else:
                    alert = ALERT(popup_reserve_to_visit, [f'ไม่พบข้อมูล\n{nationnal_id}'], button=True)
                    
                    return
                
                for row in future_tree.get_children():
                    future_tree.delete(row)

                for index, row in enumerate(prisoners_data):
                    if row[4] not in allowed_dan or row[6] != 'อยู่':
                        continue
                    future_tree.insert('', 'end', values=row)

                if len(future_tree.get_children()) == 0:
                    alert = ALERT(popup_reserve_to_visit, ['ไม่มีข้อมูลผู้ต้องขัง\nที่สามารถจองล่วงหน้าได้'], button=True)
                    
                else:
                    future_tree_container.grid(row=1, column=0, columnspan=2, padx=40, pady=10, sticky="nsew")
                    future_tree.grid(row=0, column=0, sticky='nsew', padx=(0, 8), pady=6)

                future_tree.bind('<<TreeviewSelect>>', item_select)
                future_tree_container.bind('<Configure>',lambda e: resize_tree_column())
            
            return


        def update_time_label():
            nonlocal current_time, day, month
            current_time = t.localtime()
            day = days[current_time.tm_wday]
            month = months[current_time.tm_mon - 1]
            text = f"วัน {day} ที่ {current_time.tm_mday} {month} {(current_time.tm_year)+543} เวลา {t.strftime('%H:%M:%S')}"
            date_label.configure(text=text)
            if popup_reserve_to_visit.winfo_exists():
                popup_reserve_to_visit.after(1000, update_time_label)

        # ...ลบ def run() ตัวเก่าออก...

        def on_close(e=None):
            try:
                self.zkfp2.CloseDevice()
                print('Close Device')
            except Exception as e:
                print(f'ปิดอุปกรณ์ลายนิ้วมือไม่สำเร็จ : {e}')
            try:
                popup_reserve_to_visit.destroy()
            except Exception:
                pass

        def open_device():
            main_frame_label.configure(text='กรุณาวางนิ้วมือบนเครื่องสแกนลายนิ้วมือ')
            print(f'nationnal_id in opendevice {nationnal_id}')
            try:
                self.zkfp2.Init()
                self.zkfp2.OpenDevice(0)
            except Exception as e:
                messagebox.showerror('การเชื่อมต่อเครื่อง', 'กรุณาตรวจสอบการเชื่อมต่อเครื่องสแกนลายนิ้วมือ')
                on_close()
                return
            button_visitor.grid_forget()
            main_frame_label.grid(row=0, column=0, columnspan=2, sticky='ew', padx=20, pady=20)
            threading.Thread(target=run, daemon=True).start()

        popup_reserve_to_visit = ctk.CTkToplevel(self)
        popup_reserve_to_visit.title('จองเยี่ยม')
        popup_reserve_to_visit.geometry('1920x1080+1+1')
        popup_reserve_to_visit.grab_set()
        popup_reserve_to_visit.focus()
        popup_reserve_to_visit.attributes('-fullscreen', True)

        # Card-style, modern background
        popup_reserve_to_visit.configure(fg_color="#f4f7fa")
        popup_reserve_to_visit.grid_columnconfigure(0, weight=1, uniform='popup_reserve')
        popup_reserve_to_visit.grid_rowconfigure(1, weight=1, uniform='popup_reserve')
        popup_reserve_to_visit.grid_rowconfigure(0, minsize=120, weight=0)

        # Modern top frame (header)
        top_frame = ctk.CTkFrame(
            popup_reserve_to_visit,
            fg_color="#ffffff",
            corner_radius=24,
            border_width=2,
            border_color="#e0e6ed",
            height=120
        )
        top_frame.grid(row=0, column=0, sticky='nsew', pady=(24, 8), padx=32)
        
        # Modern main frame (content)
        main_frame = ctk.CTkFrame(
            popup_reserve_to_visit,
            fg_color="#f4f7fa",
            corner_radius=24,
            border_width=2,
            border_color="#e0e6ed"
        )
        main_frame.grid(row=1, column=0, sticky='nsew', pady=(8, 24), padx=32)
        main_frame.grid_rowconfigure((0,1,2), weight=1, uniform='main_frame')
        main_frame.grid_columnconfigure((0, 1), weight=1, uniform='main_frame')

        button_visitor = ctk.CTkButton(
            main_frame,
            text='👨‍👩‍👧‍👦 กดที่นี่เพื่อเริ่มการจองเยี่ยม',
            font=('TH SarabunPSK', 72, 'bold'),
            command=lambda: open_device(),
            height=230,
            width=250,
            fg_color="#4f8cff",
            hover_color="#2d3a4b",
            text_color="#fff",
            corner_radius=18,
            border_width=2,
            border_color="#e0e6ed"
        )
        button_visitor.grid(row=0,rowspan = 3 , column=0, columnspan=2, sticky='ew', padx=20, pady=20)
        
        button_reserve_now = ctk.CTkButton(main_frame)
        button_reserve_future = ctk.CTkButton(main_frame)
        button_cancel = ctk.CTkButton(main_frame)
        # Modern date label
        date_label = ctk.CTkLabel(
            top_frame,
            font=('TH SarabunPSK', 52, 'bold'),
            text_color="#2d3a4b",
            text="",
            fg_color="#ffffff"
        )
        main_frame_label = ctk.CTkLabel(
            main_frame,
            font=('TH SarabunPSK', 72, 'bold')
        )
        date_label.pack(expand=True, fill='both', padx=16, pady=16)

        nationnal_id = None
        days = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
        months = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน",
                  "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม",
                  "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]

        current_time = t.localtime()
        day = days[current_time.tm_wday]
        month = months[current_time.tm_mon - 1]
        capture_current = None

        # Progressbar for scanning
        scan_progressbar = ctk.CTkProgressBar(
            main_frame,
            width=400,
            mode='indeterminate'
        )
        scan_progressbar.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        scan_progressbar.stop()
        scan_progressbar.grid_remove()  # Hide initially

        def show_progress():
            scan_progressbar.grid()
            scan_progressbar.start()

        def hide_progress():
            scan_progressbar.stop()
            scan_progressbar.grid_remove()

        def run():
            import time
            nonlocal capture_current, nationnal_id
            nationnal_id = None
            show_progress()
            start_time = time.time()
            scanned = False
            while True:
                try:
                    capture = self.zkfp2.AcquireFingerprint()
                except Exception as e:
                    messagebox.showerror('Error เครื่องสแกน', 'กรุณาตรวจสอบเครื่องสแกน')
                    capture = None
                if capture:
                    scanned = True
                    print('สแกนสำเร็จ', type(capture_current))
                    main_frame_label.configure(text='กำลังตรวจสอบลายนิ้วมือ...')
                    tmp, img = capture
                    capture_current = tmp
                    result = self.db.get_all_fingerprint()
                    for row in result:
                        fingerprint_in_db = row[4]
                        if fingerprint_in_db:
                            res = self.zkfp2.DBMatch(tmp, fingerprint_in_db)
                            if res > 80:
                                nationnal_id = row[0]
                                relative_data = f'{row[1]}{row[2]} {row[3]}'
                                break
                    if nationnal_id:
                        print(f'national_id = {nationnal_id}')
                        hide_progress()
                        get_relative()
                        break
                    else:
                        print('ไม่พบลายนิ้วมือในฐานข้อมูล')
                        # ไม่พบลายนิ้วมือ ติด timer เพื่อสแกนใหม่หลัง 2 วินาที
                        if popup_reserve_to_visit.winfo_exists():
                            alert = ALERT(popup_reserve_to_visit, ['ไม่พบลายนิ้วมือในฐานข้อมูล\nกรุณานำบัตรประชาชน\nติดต่อเจ้าหน้าที่'], button=False)
                            alert.after(3000,lambda: (alert.destroy(),config_label()))
                        break
                else:
                    # ไม่สามารถจับลายนิ้วมือ ติด timer เพื่อสแกนใหม่หลัง 0.5 วินาที
                    if time.time() - start_time > 20:
                        if popup_reserve_to_visit.winfo_exists():
                            config_label()
                        break
                    time.sleep(0.5)

        config_label()
        popup_reserve_to_visit.protocol("WM_DELETE_WINDOW", on_close)
        popup_reserve_to_visit.bind_all('<Alt-q>', on_close)

##############################################################################################################################################################################
    # รายการจองเยี่ยมด้วยเลขบัตรประชาชน
##############################################################################################################################################################################
    def reserve_visit_by_national_id(self):

        def config_label():
            relative_label.grid_forget()
            
            date_label.grid(row=0,column=0,columnspan=2,sticky='n', pady=10)
            insert_national_frame.grid(row=1,column=0,columnspan=2,sticky='nsew',padx=20,pady=10)
            button_frame.grid(row=2,column=0,columnspan=2,sticky='nsew',padx=20,pady=10)
            
            update_time_label()
            # get_relative()

        def update_time_label():
            text = f"วัน {day} ที่ {current_time.tm_mday} {month} {(current_time.tm_year)+543} เวลา {t.strftime('%H:%M:%S')}"
            date_label.configure(text=text)
            if popup_reserve_to_visit.winfo_exists():
                popup_reserve_to_visit.after(1000,update_time_label)

        def get_relative(state = None):
            if state:
                try:
                    self.thai_id_reader.read_card()
                    info = self.thai_id_reader.get_person_info()
                    national_id_entry.delete(0, 'end')
                    national_id_entry.insert(0, info['cid'])
                except Exception as e:
                    print(f'เกิดข้อผิดพลาดในการอ่านบัตรประชาชน : {e}')
                    messagebox.showerror('Error การอ่านบัตรประชาชน','กรุณาตรวจสอบการเชื่อมต่อเครื่องอ่านบัตรประชาชน')
                    return
            if not national_id_entry.get():
                alert = ALERT(popup_reserve_to_visit,['กรุณากรอกเลขบัตรประชาชน'],button=True)
                return
            nonlocal nationnal_id
            nationnal_id = national_id_entry.get()
            prisoners_data = self.db.get_join_relatives_and_prisoners(nationnal_id)
            # print(f'prisoners_data = {prisoners_data}')
            relative_data = self.db.get_data_for_ralative_id(nationnal_id)
            # print(f'relative_data = {relative_data}')
            relative_name = f'{relative_data[1]}{relative_data[2]} {relative_data[3]}'
            # print(relative_data)
            label_content.configure(text = f'ยินดีต้อนรับ\n{relative_name}')

            button_reserve_now = ctk.CTkButton(button_frame,
                                                text='จองเยี่ยมวันนี้',
                                                font=('TH SarabunPSK', 32, 'bold'),
                                                command=lambda: reserve_now(),
                                                height=20)
            button_reserve_future = ctk.CTkButton(button_frame,
                                                text='จองเยี่ยมล่วงหน้า',
                                                font=('TH SarabunPSK', 32, 'bold'),
                                                command=lambda: reserve_future(),
                                                height=20)
            button_cancel = ctk.CTkButton(button_frame,
                                          fg_color='red',
                                            text='ยกเลิก',
                                            font=('TH SarabunPSK', 32, 'bold'),
                                            command=lambda: (config_label(),button_reserve_now.grid_forget(),button_reserve_future.grid_forget(),button_cancel.grid_forget(),national_id_entry.delete(0, 'end'),label_content.configure(text = f'ยินดีต้อนรับ'))
                                            )
            button_reserve_now.grid(row=1,column=0,sticky='nsew',padx=20,pady=5)
            button_reserve_future.grid(row=1,column=1,sticky='nsew',padx=20,pady=5)
            button_cancel.grid(row=2,column=0,columnspan=2,padx=20,pady=5)
            now = datetime.now().time()

            def reserve_now():
                def reserve_visit(prisoner_data):
                    today_now = datetime.today().date().isoformat()
                    month_now = today_now[:7]
                    reserve = RESERVE(
                        main_window=popup_reserve_to_visit, 
                        prisoner_data=prisoner_data,
                        national_id=national_id_entry.get(),
                        to_day=today_now,
                        to_month=month_now,
                        reserve_now=True
                        )

                def item_select(_):
                    try:
                        for i in tree.selection():
                            prisoner_data = tree.item(i)['values']
                            break
                        if self.open_nextscreen_window is None or not self.open_nextscreen_window.winfo_exists():
                            self.open_nextscreen_window = reserve_visit(prisoner_data)
                        else:
                            self.open_nextscreen_window.lift()
                    except Exception as e:
                        print(f'เกิดข้อผิดพลาด item_select(_) : {e}')

                def resize_tree_column():
                    tree_container.update_idletasks()
                    total_width = tree_container.winfo_width()
                    for col, ratio in column_ratios.items():
                        tree.column(col,width=int(total_width * ratio),anchor='w')

                # Add a beautiful frame for the treeview
                tree_container = ctk.CTkFrame(
                    popup_reserve_to_visit,
                    fg_color="#f8fbff",
                    corner_radius=18,
                    border_width=2,
                    border_color="#3a7ca5"
                )
                tree_container.grid_rowconfigure(1,weight=1)
                tree_container.grid_columnconfigure(0,weight=1)

                # กำหนด style สำหรับ treeview 
                style = ttk.Style()
                style.theme_use('clam')
                style.configure('Treeview',
                    font =('TH SarabunPSK', 20),
                    rowheight = 38,
                    background="#f8fbff",
                    fieldbackground="#f8fbff",
                    bordercolor="#3a7ca5",
                    borderwidth=1
                )
                style.configure('Treeview.Heading',
                    font = ('TH SarabunPSK', 22, 'bold'),
                    background="#3a7ca5",
                    foreground="#ffffff",
                    borderwidth=2
                )
                style.map('Treeview', background=[('selected', '#b3d1ff')])

                tree = ttk.Treeview(
                    tree_container,
                    columns=('prisoner_id','f_name','l_name','level','dan','relation'),
                    show='headings',
                    height=7,
                    style='Treeview'
                )
                tree.heading('prisoner_id',text='รหัสประจำตัว')
                tree.heading('f_name',text='ชื่อ')
                tree.heading('l_name',text='นามสกุล')
                tree.heading('level',text='ชั้น')
                tree.heading('dan',text='แดน')
                tree.heading('relation',text='ความสัมพันธ์')

                tree.column('prisoner_id', anchor='center')
                tree.column('f_name', anchor='center')
                tree.column('l_name', anchor='center')
                tree.column('level', anchor='center')
                tree.column('dan', anchor='center')
                tree.column('relation', anchor='center')

                scrollbar = ttk.Scrollbar(tree_container,orient='vertical',command=tree.yview)
                tree.configure(yscrollcommand=scrollbar.set)

                button_frame.grid_forget()
                btn_cancel = ctk.CTkButton(
                    popup_reserve_to_visit,
                    text='ย้อนกลับ',
                    font=('TH SarabunPSK', 32, 'bold'),
                    fg_color="#e74c3c",
                    hover_color="#c0392b",
                    text_color="#fff",
                    corner_radius=16,
                    height=48,
                    command=lambda: (
                        tree_container.grid_forget(),
                        relative_label.grid_forget(),
                        btn_cancel.grid_forget(),
                        config_label()
                    )
                )
                btn_cancel.grid(row=3,column=0,columnspan=2,sticky='nsew',padx=60,pady=18)
                column_ratios = {
                    'prisoner_id': 0.15,
                    'f_name': 0.18,
                    'l_name': 0.18,
                    'level': 0.15,
                    'dan': 0.17,
                    'relation': 0.17,
                }

                # print('จองเยี่ยมวันนี้')
                allowed_dan_by_dan = {
                    "จันทร์" : ['6','รจช'],
                    "อังคาร" : ['5','รจช'],
                    "พุธ" : ['1','2','3','4','7','รจช'],
                    "พฤหัสบดี" : ['5','6','รจช'],
                    "ศุกร์" : ['1','2','3','4','7','รจช']        
                }
                allower_dan = allowed_dan_by_dan.get(day,[])
                # print(allower_dan)

                if prisoners_data != []:
                    print(prisoners_data)
                else:
                    alert = ALERT(popup_reserve_to_visit,[f'ไม่พบข้อมูล \n {national_id_entry.get()}'],button=True)
                    national_id_entry.delete(0, 'end')
                    return
                
                for row in tree.get_children():
                    tree.delete(row)

                for index,row in enumerate(prisoners_data):
                    if row[4] not in allower_dan or row[6] != 'อยู่':
                        continue
                    tree.insert('','end',values=row)

                if len(tree.get_children()) == 0:
                    alert = ALERT(popup_reserve_to_visit,['ไม่พบข้อมูลผู้ต้องขังที่เยี่ยมได้\nกรุณาตรวจสอบวันและเวลาเยี่ยม'],button=False)
                    alert.after(3000,lambda: (alert.destroy()))
                else:
                    relative_label.configure(text =f'กรุณากดเลือกเพื่อจองเยี่ยม' )
                    relative_label.grid(row=1,column=0,columnspan=2,sticky='nsew' )
                    tree.grid(row=1,column=0,columnspan=2,sticky='nsew')
                    tree_container.grid(row = 2,column=0,columnspan = 2,padx=20, pady=10, sticky="nsew")

                tree_container.bind('<Configure>',lambda e: resize_tree_column())
                tree.bind('<<TreeviewSelect>>',item_select)

            def reserve_future():
                def reserve_visit(prisoner_data):
                    cal_next_day = CALCULATE_NEXT_DAY()
                    today_future = cal_next_day.get_next_day()
                    month_future = today_future[:7]

                    reserve = RESERVE(
                        main_window=popup_reserve_to_visit,
                        prisoner_data=prisoner_data,
                        national_id=national_id_entry.get(),
                        to_day=today_future,
                        to_month=month_future,
                        reserve_now=False
                    )

                def item_select(_):
                    print('item_select() called')
                    try:
                        for i in future_tree.selection():
                            prisoner_data = future_tree.item(i)['values']
                            break
                        if self.open_nextscreen_window is None or not self.open_nextscreen_window.winfo_exists():
                            self.open_nextscreen_window = reserve_visit(prisoner_data)
                        else:
                            self.open_nextscreen_window.lift()
                    except Exception as e:
                        print(f'เกิดข้อผิดพลาด item_select() reserve_future: {e}')

                def resize_tree_column():
                    future_tree_container.update_idletasks()
                    total_width = future_tree_container.winfo_width()
                    for col, ratio in column_ratios.items():
                        future_tree.column(col,width=int(total_width * ratio),anchor='w')

                # Ensure previous widgets are hidden to avoid overlap
                relative_label.grid_forget()
                for widget in popup_reserve_to_visit.grid_slaves():
                    if isinstance(widget, ctk.CTkLabel) and widget.cget("text").startswith("จองเยี่ยมล่วงหน้า"):
                        widget.grid_forget()

                # Add a beautiful frame with border and background for the reservation label
                reserve_header_frame = ctk.CTkFrame(popup_reserve_to_visit, fg_color="#f0f4ff", corner_radius=20, border_width=2, border_color="#3a7ca5")
                reserve_header_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=40, sticky='nsew')
                reserve_header_frame.grid_columnconfigure(0, weight=1)

                cal_next_day = CALCULATE_NEXT_DAY()
                next_day = cal_next_day.get_next_day()
                dt = datetime.strptime(next_day, '%Y-%m-%d')
                # แปลงวันที่เป็น วัน เดือน ปี (พ.ศ.) ภาษาไทย
                thai_days = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
                thai_months = [
                    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
                    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
                ]
                weekday = thai_days[dt.weekday()]
                month = thai_months[dt.month - 1]
                year_th = dt.year + 543
                date_thai = f"วัน{weekday} ที่ {dt.day} {month} {year_th}"

                content_reserve = ctk.CTkLabel(
                    reserve_header_frame,
                    text=f'จองเยี่ยมล่วงหน้าสำหรับ {date_thai}',
                    font=('TH SarabunPSK', 36, 'bold'),
                    text_color="#2d3a4b"
                )
                content_reserve.grid(row=0, column=0, pady=10, padx=10, sticky='nsew')

                # Add a shadowed, rounded frame for the treeview
                future_tree_container = ctk.CTkFrame(popup_reserve_to_visit, fg_color="#ffffff", corner_radius=18, border_width=2, border_color="#3a7ca5")
                future_tree_container.grid_rowconfigure(0, weight=1)
                future_tree_container.grid_columnconfigure(0, weight=1)
                
                # กำหนด style สำหรับ treeview 
                style = ttk.Style()
                style.theme_use('clam')
                style.configure('Treeview',
                    font =('TH SarabunPSK', 20),
                    rowheight = 38,
                    background="#f8fbff",
                    fieldbackground="#f8fbff",
                    bordercolor="#3a7ca5",
                    borderwidth=1
                )
                style.configure('Treeview.Heading',
                    font = ('TH SarabunPSK', 22, 'bold'),
                    background="#3a7ca5",
                    foreground="#ffffff",
                    borderwidth=2
                )
                style.map('Treeview', background=[('selected', '#b3d1ff')])

                # สร้าง treeview สำหรับจองล่วงหน้า
                future_tree = ttk.Treeview(
                    future_tree_container,
                    columns=('prisoner_id','f_name','l_name','level','dan','relation'),
                    show='headings',
                    height=7,
                    style='Treeview'
                )
                future_tree.heading('prisoner_id',text='รหัสประจำตัว')
                future_tree.heading('f_name',text='ชื่อ')
                future_tree.heading('l_name',text='นามสกุล')
                future_tree.heading('level',text='ชั้น')
                future_tree.heading('dan',text='แดน')
                future_tree.heading('relation',text='ความสัมพันธ์')
                future_tree.column('prisoner_id', anchor='center')
                future_tree.column('f_name', anchor='center')
                future_tree.column('l_name', anchor='center')
                future_tree.column('level', anchor='center')
                future_tree.column('dan', anchor='center')
                future_tree.column('relation', anchor='center')
                future_scrollbar = ttk.Scrollbar(future_tree_container, orient='vertical', command=future_tree.yview)
                future_tree.configure(yscrollcommand=future_scrollbar.set)
                future_scrollbar.grid(row=0, column=1, sticky='ns', pady=6)

                button_frame.grid_forget()
                btn_cancel = ctk.CTkButton(
                    popup_reserve_to_visit,
                    text='ย้อนกลับ',
                    font=('TH SarabunPSK', 32, 'bold'),
                    fg_color="#e74c3c",
                    hover_color="#c0392b",
                    text_color="#fff",
                    corner_radius=16,
                    height=48,
                    command=lambda: (
                        future_tree_container.grid_forget(),
                        reserve_header_frame.grid_forget(),
                        btn_cancel.grid_forget(),
                        config_label()
                    )
                )
                btn_cancel.grid(row=4, column=0, columnspan=2, sticky='nsew', padx=60, pady=18)
                # ดึงข้อมูลผู้ต้องขังที่สามารถจองล่วงหน้าได้ (ตัวอย่าง: ใช้ prisoners_data เดิม)

                # กำหนดความกว้าง column
                column_ratios = {
                    'prisoner_id': 0.15,
                    'f_name': 0.18,
                    'l_name': 0.18,
                    'level': 0.15,
                    'dan': 0.17,
                    'relation': 0.17,
                }
                allowed_dan_by_dan={
                    "อาทิตย์" : [],
                    "จันทร์" : ['6','รจช'],
                    "อังคาร" : ['5','รจช'],
                    "พุธ" : ['1','2','3','4','7','รจช'],
                    "พฤหัสบดี" : ['5','6','รจช'],
                    "ศุกร์" : ['1','2','3','4','7','รจช'],
                    "เสาร์" : []
                }
                # print(days)
                try:
                    allowed_dan = allowed_dan_by_dan.get(weekday)
                except Exception as e:
                    print(f'เกิดข้อผิดพลาด {e}')
                
                if prisoners_data != []:
                    print(prisoners_data)
                    # ถ้าไม่มีข้อมูลผู้ต้องขังที่สามารถจองล่วงหน้าได้
                    # future_tree.insert('', 'end', values=('ไม่มีข้อมูล', '', '', '', '', ''))
                else:
                    alert = ALERT(popup_reserve_to_visit, [f'ไม่พบข้อมูล\n{national_id_entry.get()}'], button=True)
                    national_id_entry.delete(0, 'end')
                    return
                
                for row in future_tree.get_children():
                    future_tree.delete(row)

                for index, row in enumerate(prisoners_data):
                    if row[4] not in allowed_dan or row[6] != 'อยู่':
                        continue
                    future_tree.insert('', 'end', values=row)

                if len(future_tree.get_children()) == 0:
                    print(weekday,type(weekday))
                    alert = ALERT(popup_reserve_to_visit, ['ไม่มีข้อมูลผู้ต้องขัง\nที่สามารถจองล่วงหน้าได้'], button=True)
                    national_id_entry.delete(0, 'end')
                else:
                    relative_label.configure(text=f'กรุณากดเลือกเพื่อจองเยี่ยม')
                    relative_label.grid(row=1, column=0, columnspan=2, pady=10, padx=20, sticky='nsew')
                    future_tree_container.grid(row=3, column=0, columnspan=2, padx=40, pady=10, sticky="nsew")
                    future_tree.grid(row=0, column=0, sticky='nsew', padx=(0, 8), pady=6)

                future_tree.bind('<<TreeviewSelect>>', item_select)
                future_tree_container.bind('<Configure>',lambda e: resize_tree_column())
            return

        def on_close(e = None):
            popup_reserve_to_visit.destroy()

        popup_reserve_to_visit = ctk.CTkToplevel(self) 
        popup_reserve_to_visit.title('จองเยี่ยม')
        popup_reserve_to_visit.geometry('980x640+1+1')
        popup_reserve_to_visit.grab_set()
        popup_reserve_to_visit.focus()
        popup_reserve_to_visit.configure(fg_color='#f4f7fa')  # เพิ่มสีพื้นหลังให้สอดคล้องกับธีม
        popup_reserve_to_visit.grid_columnconfigure((0,1),weight=1,uniform='popup_reserve')
        popup_reserve_to_visit.grid_rowconfigure(1,weight=0,uniform='popup_reserve')
        insert_national_frame = ctk.CTkFrame(popup_reserve_to_visit, fg_color='#ffffff', corner_radius=16, border_width=2, border_color='#e3eefa')  # เพิ่มสีและมุมมน
        insert_national_frame.grid_rowconfigure(0,weight=1,uniform='popup_reserve')
        insert_national_frame.grid_columnconfigure((0,1,2),weight=1,uniform='popup_reserve')
        
        button_frame = ctk.CTkFrame(popup_reserve_to_visit, fg_color='#f8fbff', corner_radius=16, border_width=2, border_color='#b3d1ff')
        button_frame.grid_rowconfigure((0,1,2),weight=1,uniform='popup_reserve',minsize=150)
        button_frame.grid_columnconfigure((0,1),weight=1,uniform='popup_reserve')

        insert_label = ctk.CTkLabel(insert_national_frame,text='กรุณากรอกเลขบัตรประชาชน :',font=('TH SarabunPSK', 32, 'bold'),text_color='#2d3a4b')
        insert_label.grid(row=0,column=0,pady=10,sticky='e',padx = 10)
        btn_read_id = ctk.CTkButton(insert_national_frame,
                                    text='อ่านข้อมูล',
                                    font=('TH SarabunPSK', 32, 'bold'),
                                    fg_color='#4f8cff', hover_color='#2d3a4b', text_color='#ffffff',
                                    command=lambda : get_relative(True))
        btn_read_id.grid(row=0,column=2,pady=10,sticky='w',padx = 10)
        label_content = ctk.CTkLabel(button_frame,text='ยินดีต้อนรับ',font=('TH SarabunPSK', 48, 'bold'),text_color='#2d3a4b')
        label_content.grid(row = 0,column = 0,columnspan = 3 ,sticky = 'nsew',pady = 10,padx = 10)
        national_id_entry = ctk.CTkEntry(insert_national_frame,font=('TH SarabunPSK', 32, 'bold'),placeholder_text='เลขบัตรประชาชน 13 หลัก',width=300,
            fg_color='#ffffff', text_color='#2d3a4b', border_color='#4f8cff', border_width=2)
        national_id_entry.grid(row=0,column=1,pady=10,sticky='ew',padx = 10)
        national_id_entry.bind('<Return>',lambda e: get_relative())
        national_id_entry.bind('<KP_Enter>',lambda e: get_relative())

        # label_content = ctk.CTkLabel(popup_reserve_to_visit,text='',font=('TH SarabunPSK', 52, 'bold'))
        date_label = ctk.CTkLabel(popup_reserve_to_visit,font=('TH SarabunPSK', 52, 'bold'),text_color='#2d3a4b')
        relative_label = ctk.CTkLabel(popup_reserve_to_visit,font=('TH SarabunPSK', 46, 'bold'),text_color='#2d3a4b')

        nationnal_id = None
        days = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์","อาทิตย์"]
        months = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน",
                    "พฤษภาคม","มิถุนายน","กรกฎาคม", "สิงหาคม",
                    "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]

        current_time = t.localtime()
        day = days[current_time.tm_wday]
        month = months[current_time.tm_mon - 1]

        config_label()

        popup_reserve_to_visit.protocol("WM_DELETE_WINDOW", on_close)
##############################################################################################################################################################################
    # รายงานการเยี่ยม
##############################################################################################################################################################################
    def report_visits(self):
        # helper สำหรับเรียงตาม channel
        def _channel_key(val):
            try:
                return int(val)
            except Exception:
                return 10**9  # ค่ามากไว้ท้ายสุด

        def _sort_rows_by_channel(rows):
            try:
                return sorted(rows, key=lambda r: _channel_key(r[11] if len(r) > 11 else None))
            except Exception:
                return rows

        def resize_tree_column():
            tree_container.update_idletasks()
            total_width = tree_container.winfo_width()
            # กำหนด anchor แต่ละคอลัมน์
            column_anchors = {
                'time_stamp': 'center',
                'date_visit': 'center', 
                'time_visit': 'center',
                'prisoner_id': 'w',
                'dan': 'w',
                'relation_id_1': 'w',
                'relation_id_2': 'w',
                'relation_id_3': 'w',
                'relation_id_4': 'w',
                'relation_id_5': 'w',
                'channel': 'center'
            }
            
            for col, ratio in column_ratios.items():
                anchor_type = column_anchors.get(col, 'center')  # default เป็น 'w'
                tree.column(col, width=int(total_width * ratio), anchor=anchor_type)

        def print_table():
            try:
                # สร้าง pdf
                temp_pdf = tempfile.mktemp(".pdf")
                c = canvas.Canvas(temp_pdf, pagesize=landscape(A4))
                width, height = landscape(A4)
                
                # ฟรอน และ ระยะห่าง
                c.setFont("TH SarabunPSK", 18)
                c.drawCentredString(width / 2, height - 1.5 * cm, f"รายงานการเยี่ยม วันที่ {date_now} เวลาเยี่ยม {combo_round.get()}")
                c.setFont("TH SarabunPSK", 11)
                
                # หัวตารางและความกว้าง
                columns = tree["columns"]
                headers = [tree.heading(col)["text"] for col in columns if col != 'visit_id']
                
                # ปรับขนาด column ให้พอดีกับหน้ากระดาษ
                available_width = width - 2*cm  # หักขอบซ้าย-ขวา
                num_columns = len(headers)
                
                # กำหนดความกว้างแต่ละ column ตามเนื้อหา
                col_widths = []
                if num_columns == 11:  # จำนวน column ที่แสดง (ไม่รวม visit_id)
                    col_widths = [
                        available_width * 0.10,  # Time Stamp
                        available_width * 0.07,  # วันที่จอง
                        available_width * 0.07,  # เวลาเยี่ยม
                        available_width * 0.14,  # ชื่อผู้ต้องขัง
                        available_width * 0.035,  # แดน
                        available_width * 0.11,  # ญาติคนที่ 1
                        available_width * 0.11,  # ญาติคนที่ 2
                        available_width * 0.11,  # ญาติคนที่ 3
                        available_width * 0.11,  # ญาติคนที่ 4
                        available_width * 0.11,  # ญาติคนที่ 5
                        available_width * 0.035,  # ช่อง
                    ]
                else:
                    # ถ้าจำนวน column ไม่ใช่ 11 ให้แบ่งเท่า ๆ กัน
                    col_widths = [available_width / num_columns] * num_columns
                
                # ตำแหน่งเริ่ม
                start_x = 1*cm
                start_y = height - 3 * cm
                row_height = 0.8*cm
                
                # วาดหัวตาราง
                y = start_y
                x = start_x
                for i, header in enumerate(headers):
                    c.setFillColorRGB(0.31, 0.55, 0.80)  # blue header
                    c.rect(x, y, col_widths[i], row_height, stroke=1, fill=1)
                    c.setFillColorRGB(1, 1, 1)
                    c.drawString(x+0.2*cm, y+0.3*cm, header)
                    x += col_widths[i]
                    
                # วาดข้อมูล
                y -= row_height
                for child_id in tree.get_children():
                    x = start_x
                    values = tree.item(child_id, "values")
                    for i, value in enumerate(values[1:]):  # ข้าม visit_id
                        c.setFillColorRGB(0.97, 0.98, 1) if y % 2 == 0 else c.setFillColorRGB(1, 1, 1)
                        c.rect(x, y, col_widths[i], row_height, stroke=1, fill=1)
                        c.setFillColorRGB(0, 0, 0)
                        text = str(value)
                        
                        # ตัดข้อความถ้ายาวเกินไป
                        max_width = col_widths[i] - 0.4*cm
                        text_width = c.stringWidth(text, "TH SarabunPSK", 11)
                        if text_width > max_width:
                            # ตัดข้อความและเพิ่ม ...
                            while text_width > max_width and len(text) > 3:
                                text = text[:-1]
                                text_width = c.stringWidth(text + "...", "TH SarabunPSK", 11)
                            text = text + "..."
                        
                        # จัดตำแหน่งข้อความ
                        if text.isdigit():
                            # จัดขวาสำหรับตัวเลข
                            text_width = c.stringWidth(text, "TH SarabunPSK", 11)
                            c.drawString(x+col_widths[i]-text_width-0.2*cm, y+0.3*cm, text)
                        else:
                            # จัดซ้ายสำหรับข้อความ
                            c.drawString(x+0.2*cm, y+0.3*cm, text)
                        x += col_widths[i]
                    y -= row_height
                    
                    # ตรวจสอบถ้าใกล้หมดหน้า ให้สร้างหน้าใหม่
                    if y < 2*cm:
                        c.showPage()
                        c.setFont("TH SarabunPSK", 11)
                        y = height - 2*cm
                
                c.save()
                os.startfile(temp_pdf)
                messagebox.showinfo('กำลังพิมพ์', 'สั่งพิมพ์เรียบร้อย')
                time.sleep(2)
                try:
                    os.remove(temp_pdf)
                except Exception:
                    pass
            except Exception as e:
                messagebox.showerror('ข้อผิดพลาด', f'ไม่สามารถพิมพ์ได้ :\n{e}')
            # try:
            #     # สร้าง pdf
            #     temp_pdf = tempfile.mktemp(".pdf")
            #     c = canvas.Canvas(temp_pdf, pagesize=landscape(A4))
            #     width, height = landscape(A4)
            #     # ฟรอน และ ระยะห่าง
            #     c.setFont("TH SarabunPSK", 18)
            #     c.drawCentredString(width / 2, height - 1.5 * cm, f"รายงานการเยี่ยม วันที่ {date_now} เวลาเยี่ยม {combo_round.get()}")
            #     c.setFont("TH SarabunPSK", 11)
            #     # หัวตารางและความกว้าง
            #     columns = tree["columns"]
            #     col_widths = [3.07*cm] * (len(columns)-1)  # -1 เพราะจะไม่ print visit_id
            #     headers = [tree.heading(col)["text"] for col in columns if col != 'visit_id']
            #     # ตำแหน่งเริ่ม
            #     start_x = 1*cm
            #     start_y = height - 3 * cm
            #     row_height = 0.8*cm
            #     # วาดหัวตาราง
            #     y = start_y
            #     x = start_x
            #     for i, header in enumerate(headers):
            #         c.setFillColorRGB(0.31, 0.55, 0.80)  # blue header
            #         c.rect(x, y, col_widths[i], row_height, stroke=1, fill=1)
            #         c.setFillColorRGB(1, 1, 1)
            #         c.drawString(x+0.2*cm, y+0.3*cm, header)
            #         x += col_widths[i]
            #     # วาดข้อมูล
            #     y -= row_height
            #     for child_id in tree.get_children():
            #         x = start_x
            #         values = tree.item(child_id, "values")
            #         for i, value in enumerate(values[1:]):
            #             c.setFillColorRGB(0.97, 0.98, 1) if y % 2 == 0 else c.setFillColorRGB(1, 1, 1)
            #             c.rect(x, y, col_widths[i], row_height, stroke=1, fill=1)
            #             c.setFillColorRGB(0, 0, 0)
            #             text = str(value)
            #             if text.isdigit():
            #                 text_width = c.stringWidth(text, "TH SarabunPSK", 10)
            #                 c.drawString(x+col_widths[i]-text_width-0.2*cm, y+0.3*cm, text)
            #             else:
            #                 c.drawString(x+0.2*cm, y+0.3*cm, text)
            #             x += col_widths[i]
            #         y -= row_height
            #     c.save()
            #     os.startfile(temp_pdf)
            #     messagebox.showinfo('กำลังพิมพ์', 'สั่งพิมพ์เรียบร้อย')
            #     time.sleep(2)
            #     try:
            #         os.remove(temp_pdf)
            #     except Exception:
            #         pass
            # except Exception as e:
            #     messagebox.showerror('ข้อผิดพลาด', f'ไม่สามารถพิมพ์ได้ :\n{e}')

        def get_visits(keyword = None):
            result = []
            if keyword is None:
                print(f'Searching for visits with keyword: {keyword}')
                # tree.grid_forget()
                round_time = combo_round.get()
                year = year_var.get()
                month = month_dict[month_var.get()]
                day = day_var.get()
                round_date = f"{year}-{month}-{day}"
                # print(f'round_date = {round_date} and round_time = {round_time}')
                data = [round_date, round_time]
                result = self.db.get_visits_on_db(data)
                print(f'data on get visits = {result}')
            else:
                print(f'Searching for visits with keyword: {keyword}')
                if keyword == '':
                    alert = ALERT(self, ['กรุณากรอก คำค้นหา'], button=True)
                    return
                # เพิ่มโค้ดค้นหาด้วย keyword

                all_results = self.db.get_visits_all_on_db()

                print(f'ค้นหาด้วย keyword = {keyword} และ all_results = {all_results}')
                # กรองข้อมูลด้วย keyword (ค้นหาชื่อผู้ต้องขัง)

                if all_results and isinstance(all_results, (list, tuple)):
                    
                    for row in all_results:
                        name = str(row[4])
                        if difflib.SequenceMatcher(None,keyword.lower(),name.lower()).ratio() > 0.4:
                            result.append(row)
                else:
                    result = []
            # เรียงผลลัพธ์ตาม channel ก่อนใส่ลงตาราง
            result = _sort_rows_by_channel(result)
            
            for row in tree.get_children():
                tree.delete(row)
            
            # ตรวจสอบว่า result เป็น list หรือไม่ ถ้าเป็น False (error) จะไม่ iterate
            if result and isinstance(result, (list, tuple)):
                for row in result:
                    # แทนที่ค่า None ด้วย "-"
                    processed_row = ["-" if value is None else value for value in row]
                    tree.insert('', 'end', values=processed_row)
            else:
                print("No data found or error occurred")
                # แสดงข้อความว่าไม่พบข้อมูล
                tree.insert('', 'end', values=('ไม่พบข้อมูล', '', '', '', '', '', '', '', '', '', ''))
            tree_container.grid(row=2, column=0, sticky='nsew')
            tree.grid(row=0, column=0, sticky='new', padx=6, pady=(8, 0))
            # ปุ่มพิมพ์แบบลอยขวา
            button_print = ctk.CTkButton(table_frame, text='พิมพ์', font=('TH SarabunPSK', 20, 'bold'), fg_color="#4f8cff", hover_color="#2d3a4b", text_color="#fff", corner_radius=12, command=lambda: print_table())
            button_print.grid(row=1, column=0, padx=16, pady=(8, 8))
       
        @require_admin
        def on_right_click(event):
            nonlocal popup_window_right_click
            selected = tree.identify_row(event.y)
            if not selected:
                return
            values = tree.item(selected)['values']
            print(f'values = {values}')
            # ฟังก์ชันสำหรับเมนูคลิกขวา
            def move_round():

                def move_round():
                    round_selected = time_visit.get()
                    date_current = datetime.now().strftime("%Y-%m-%d")
                    print(date_current)
                    print(f'move round {round_selected}')
                    result_count_round_visit = self.db.get_count_visit_on_round(round_selected, date_current)
                    print(f'จำนวนคนที่จองรอบ {result_count_round_visit}')
                    channel_on_db = self.db.get_channel(date_current,round_selected)
                    print(f'channel_on_db = {channel_on_db} and type = {type(channel_on_db)}')
                    sorted_channel_on_db = sorted(channel_on_db)
                    channel_empty = 1

                    for index,value in enumerate(sorted_channel_on_db):
                        print(f'index,value {index}{value}')
                        if index+1 != int(value):
                            channel_empty = index + 1
                            print(f'channel ช่องว่าง = {channel_empty}')
                            break
                        elif index == len(sorted_channel_on_db) - 1:
                            channel_empty = index + 2
                            print(f'channel ตัวสุดท้าย = {channel_empty}')
                    print(f'ค่าที่เติม = {channel_empty}')
                    if result_count_round_visit >=15:
                        alert = ALERT(move_round_pupup,['รอบเต็ม\nกรุณาเลือกรอบใหม่'],text_color='red',button=True)
                        alert.after(3000,lambda: (alert.destroy(),move_round_pupup.destroy()))
                        return
                    else:
                        result_move_round = self.db.update_visit_round_and_channel(round_selected,channel_empty,values[0])
                        if result_move_round:
                            alert = ALERT(move_round_pupup,[f'ย้ายรอบของ\n{values[4]}\nรอบใหม่เวลา {round_selected}'],text_color='black',button=True)
                            if alert.show():
                                move_round_pupup.destroy()
                                get_visits()

                popup_window_right_click.destroy()
                print('ย้ายรอบ')
                print('fn move_round ********* ',type(values[3]),values[3])
                if values[3] == '12:00:00':
                    alert = ALERT(self,msg=['เรือนจำชั่วคราวไม่สามารถย้ายรอบได้'],button=True)
                    return
                move_round_pupup = ctk.CTkToplevel()
                move_round_pupup.configure(fg_color='#f4f7fa')  # เพิ่มสีพื้นหลังให้สอดคล้องกับธีม
                move_round_pupup.title('ย้ายรอบเยี่ยม')
                move_round_pupup.geometry('500x200+400+50')
                move_round_pupup.grab_set()
                move_round_pupup.focus()

                move_round_pupup.grid_columnconfigure(0,weight=1,uniform='move_round')
                move_round_pupup.grid_rowconfigure((0,1,2),weight=1,uniform='move_round')
                label_content = ctk.CTkLabel(move_round_pupup,text=f'ย้ายรอบเยี่ยม\n{values[4]}',font=('TH SarabunPSK',32,'bold'),text_color='#2d3a4b')
                label_content.grid(row = 0 , column = 0 ,sticky = 'ns')
                time_visit = ctk.CTkOptionMenu(move_round_pupup,
                                                values=['09:30:00','10:00:00','10:30:00','11:00:00','13:15:00','13:45:00','14:15:00'],
                                                font=('TH SarabunPSK',18),
                                                dropdown_font=('TH SarabunPSK',18),
                                                fg_color='#ffffff', button_color='#4f8cff', text_color='#222')
                time_visit.grid(row=1,column=0,sticky='ns',padx = 40,pady = 20)
                button = ctk.CTkButton(move_round_pupup,text='ยืนยัน',width=140,font=('TH SarabunPSK',18),
                    fg_color='#4f8cff', hover_color='#2d3a4b', text_color='#ffffff',
                    command=lambda: move_round())
                button.grid(row = 2,column = 0 ,sticky = 'ns',padx = 20,pady = 20)

            def remove_round():
                popup_window_right_click.destroy()
                print('ยกเลิกรอบ')
                result_remove = self.db.remove_visit(values[0])
                if result_remove:
                    alert = ALERT(self,[f'ยกเลิกรอบเยี่ยมของ\n{values[4]}\nสำเร็จ'],text_color='black',button=True)
                    if alert.show():
                        get_visits()
                else:
                    alert = ALERT(self,['ไม่สามารถยกเลิกรอบเยี่ยมได้'],text_color='red',button=True)
                    
            def add_visit():
                def read_card():
                    try:
                        self.thai_id_reader.read_card()
                        info = self.thai_id_reader.get_person_info()
                    except Exception as e:
                        print(f'เกิดข้อผิดพลาดในการอ่านบัตรประชาชน : {e}')
                        messagebox.showerror('Error การอ่านบัตรประชาชน','กรุณาตรวจสอบการเชื่อมต่อเครื่องอ่านบัตรประชาชน')
                        return 
                    return info['cid']
                
                def save_to_db():
                    visit_id = values[0]
                    data_relative = []
                    data_relative.append(data_visit_no_1.cget('text'))
                    data_relative.append(data_visit_no_2.cget('text'))   
                    data_relative.append(data_visit_no_3.cget('text'))
                    data_relative.append(data_visit_no_4.cget('text'))
                    data_relative.append(data_visit_no_5.cget('text'))
                    data_relative.append(visit_id)
                    result_add_relatives =  self.db.add_relative_to_visits(data_relative)
                    if result_add_relatives:
                        alert = ALERT(add_visit_popup,[f'เพิ่มชื่อญาติเยี่ยมสำเร็จ'],text_color='black',button=True)
                        if alert.show():
                            add_visit_popup.destroy()
                            get_visits()
                    else:
                        alert = ALERT(add_visit_popup,[f'ไม่สามารถเพิ่มชื่อญาติเยี่ยมได้'],text_color='red',button=True)
        
                result_get_visits = self.db.get_visit_by_id(values[0])
                relationship = self.db.get_join_prisoners_and_relatives(result_get_visits[4])
                print(result_get_visits)
                print(relationship)
                popup_window_right_click.destroy()
                add_visit_popup = ctk.CTkToplevel()
                add_visit_popup.configure(fg_color='#f4f7fa')  # เพิ่มสีพื้นหลังให้สอดคล้องกับธีม
                add_visit_popup.title('เพิ่มชื่อญาติเยี่ยม')
                add_visit_popup.geometry('720x760+400+50')  
                add_visit_popup.grab_set()
                add_visit_popup.focus()

                # Card-style, modern background
                add_visit_popup.configure(fg_color="#f4f7fa")
                add_visit_popup.grid_columnconfigure(0, weight=1)
                add_visit_popup.grid_rowconfigure(0, weight=1)

                # Main card frame
                card_frame = ctk.CTkFrame(
                    add_visit_popup,
                    fg_color="#ffffff",
                    corner_radius=22,
                    border_width=2,
                    border_color="#4f8cff"
                )
                card_frame.grid(row=0, column=0, sticky="nsew", padx=28, pady=28)
                card_frame.grid_columnconfigure((0,1), weight=1)
                for i in range(9):
                    card_frame.grid_rowconfigure(i, weight=1)

                # Header
                label_content = ctk.CTkLabel(
                    card_frame,
                    text=f'เพิ่มชื่อญาติเยี่ยม\n{values[3]} น.  {values[4]}',
                    font=('TH SarabunPSK', 34, 'bold'),
                    text_color="#2d3a4b",
                    fg_color="#ffffff"
                )
                label_content.grid(row=0, column=0, columnspan=2, sticky='nsew', pady=(18, 4),padx = 10)
                date_label = ctk.CTkLabel(card_frame, text=f'วันที่จอง {values[2]}', font=('TH SarabunPSK', 22), text_color="#4f8cff")
                date_label.grid(row=1, column=0, columnspan=2, sticky='nsew', pady=(0, 2),padx = 5)
                time_label = ctk.CTkLabel(card_frame, text=f'เวลาเยี่ยม {values[3]} น.', font=('TH SarabunPSK', 22), text_color="#4f8cff")
                time_label.grid(row=2, column=0, columnspan=2, sticky='nsew', pady=(0, 8),padx = 5)

                # Labels for relatives
                label_style = {'font':('TH SarabunPSK',24), 'text_color':'#2d3a4b', 'fg_color':'#ffffff'}
                visit_no_1 = ctk.CTkLabel(card_frame, text='ญาติคนที่ 1 :', **label_style)
                visit_no_1.grid(row=3, column=0, sticky='e', padx=(18, 8), pady=8)
                visit_no_2 = ctk.CTkLabel(card_frame, text='ญาติคนที่ 2 :', **label_style)
                visit_no_2.grid(row=4, column=0, sticky='e', padx=(18, 8), pady=8)
                visit_no_3 = ctk.CTkLabel(card_frame, text='ญาติคนที่ 3 :', **label_style)
                visit_no_3.grid(row=5, column=0, sticky='e', padx=(18, 8), pady=8)
                visit_no_4 = ctk.CTkLabel(card_frame, text='ญาติคนที่ 4 :', **label_style)
                visit_no_4.grid(row=6, column=0, sticky='e', padx=(18, 8), pady=8)
                visit_no_5 = ctk.CTkLabel(card_frame, text='ญาติคนที่ 5 :', **label_style)
                visit_no_5.grid(row=7, column=0, sticky='e', padx=(18, 8), pady=8)

                # Data labels for relatives
                data_label_style = {'font':('TH SarabunPSK',24), 'text_color':'#4f8cff', 'fg_color':'#f8fbff'}
                data_visit_no_1 = ctk.CTkLabel(card_frame, text='', **data_label_style)
                data_visit_no_1.grid(row=3, column=1, sticky='w', padx=(8, 18), pady=8)
                data_visit_no_2 = ctk.CTkLabel(card_frame, text='', **data_label_style)
                data_visit_no_2.grid(row=4, column=1, sticky='w', padx=(8, 18), pady=8)
                data_visit_no_3 = ctk.CTkLabel(card_frame, text='', **data_label_style)
                data_visit_no_3.grid(row=5, column=1, sticky='w', padx=(8, 18), pady=8)
                data_visit_no_4 = ctk.CTkLabel(card_frame, text='', **data_label_style)
                data_visit_no_4.grid(row=6, column=1, sticky='w', padx=(8, 18), pady=8)
                data_visit_no_5 = ctk.CTkLabel(card_frame, text='', **data_label_style)
                data_visit_no_5.grid(row=7, column=1, sticky='w', padx=(8, 18), pady=8)

                # Buttons
                button_add_visit = ctk.CTkButton(
                    card_frame,
                    text='เพิ่ม',
                    font=('TH SarabunPSK', 24, 'bold'),
                    fg_color="#4f8cff",
                    hover_color="#2d3a4b",
                    text_color="#fff",
                    corner_radius=14,
                    command=save_to_db
                )
                button_add_visit.grid(row=8, column=0, padx=18, pady=18, sticky='ew')
                button_cancel = ctk.CTkButton(
                    card_frame,
                    text='ยกเลิก',
                    fg_color='#e74c3c',
                    hover_color='#c0392b',
                    font=('TH SarabunPSK', 24, 'bold'),
                    text_color="#fff",
                    corner_radius=14,
                    command=lambda:add_visit_popup.destroy()
                )
                button_cancel.grid(row=8, column=1, padx=18, pady=18, sticky='ew')

                # Fill data
                for index, data in enumerate(result_get_visits):
                    print(f'index = {index} data = {data}')
                    if index == 5 and data != None:
                        data_visit_no_1.configure(text=f'{data}')
                    elif index == 6 and data != None:
                        data_visit_no_2.configure(text=f'{data}')
                    elif index == 7 and data != None:
                        data_visit_no_3.configure(text=f'{data}')
                    elif index == 8 and data != None:
                        data_visit_no_4.configure(text=f'{data}')
                    elif index == 9 and data != None:
                        data_visit_no_5.configure(text=f'{data}')

                # Add entry and "เพิ่มญาติ" button if empty
                def add_entry_and_btn_if_empty(data_label, row):
                    if data_label.cget('text') == '':
                        entry = ctk.CTkEntry(
                            card_frame,
                            font=('TH SarabunPSK', 22),
                            width=160,
                            placeholder_text='กรอกเลขญาติ'
                        )
                        entry.grid(row=row, column=1, sticky='w', padx=(8, 2), pady=8)

                        # บันทึกข้อมูลลงฐานข้อมูล


                        # เช็คข้อมูล
                        def check_label_visit(relative_id):
                            all_label = list()
                            all_label.append(data_visit_no_1.cget('text'))
                            all_label.append(data_visit_no_2.cget('text'))
                            all_label.append(data_visit_no_3.cget('text'))
                            all_label.append(data_visit_no_4.cget('text'))
                            all_label.append(data_visit_no_5.cget('text'))

                            result_visit = self.db.prisoner_id_on_table_visits(values[0])
                            result_count = self.db.count_relative(result_visit,relative_id)

                            if result_count == 0:
                                alert = ALERT(add_visit_popup,msg=['ไม่พบข้อมูลและความสัมพันธ์'],button=True)
                                return False
                            for i in all_label:
                                print(i,relative_id)
                                if i == relative_id:
                                    alert = ALERT(add_visit_popup,msg=[f'หมายเลข {relative_id}\nมีการจองเยี่ยมแล้ว'],button=True)
                                    return False
                            return True

                        def on_add():
                            relative_id = entry.get().strip()
                            if not relative_id:
                                relative_id = read_card()
                                print(relative_id)
                                if not relative_id:
                                    return
                                entry.insert(0, relative_id)
                            result_check_data = check_label_visit(relative_id)
                            if not result_check_data:
                                entry.delete(0, 'end')
                                return
                            entry.grid_forget()
                            btn.grid_forget()
                            data_label.configure(text=relative_id)

                        btn = ctk.CTkButton(
                            card_frame,
                            text='เพิ่มญาติ',
                            font=('TH SarabunPSK', 22, 'bold'),
                            fg_color="#f1c40f",
                            hover_color="#f39c12",
                            text_color="#2d3a4b",
                            corner_radius=12,
                            command=on_add
                        )
                        btn.grid(row=row, column=1, sticky='e', padx=(90, 18), pady=8)

                add_entry_and_btn_if_empty(data_visit_no_1, 3)
                add_entry_and_btn_if_empty(data_visit_no_2, 4)
                add_entry_and_btn_if_empty(data_visit_no_3, 5)
                add_entry_and_btn_if_empty(data_visit_no_4, 6)
                add_entry_and_btn_if_empty(data_visit_no_5, 7)

            nonlocal popup_window_right_click
            try:
                popup_window_right_click.destroy()
            except:
                pass

            # เลือกแถวในตาราง tree
            selected = tree.identify_row(event.y)
            if not selected:
                return
            
            tree.selection_set(selected)
            values = tree.item(selected)['values']
            
            popup_window_right_click = ctk.CTkToplevel()
            popup_window_right_click.configure(fg_color='#f4f7fa')  # เพิ่มสีพื้นหลังให้สอดคล้องกับธีม
            popup_window_right_click.overrideredirect(True)
            popup_window_right_click.geometry(f'+{event.x_root}+{event.y_root}')
            popup_window_right_click.configure(fg_color = '#f8fbff', border_width=2, border_color='#4f8cff')
            # ปรับปุ่มเมนูคลิกขวาให้ดูทันสมัย
            btn_style = {'font':('TH SarabunPSK',18,'bold'), 'width':160, 'corner_radius':10, 'height':36}
            ctk.CTkButton(popup_window_right_click, text='เพิ่มชื่อญาติเยี่ยม', fg_color="#4f8cff", hover_color="#2d3a4b", text_color="#fff", command=add_visit, **btn_style).pack(padx=10, pady=(10,5))
            ctk.CTkButton(popup_window_right_click, text='ย้ายรอบ', fg_color="#f1c40f", hover_color="#f39c12", text_color="#2d3a4b", command=move_round, **btn_style).pack(padx=10, pady=(10,5))
            ctk.CTkButton(popup_window_right_click, text='ยกเลิกรอบ', fg_color='#e74c3c', hover_color='#c0392b', text_color="#fff", command=remove_round, **btn_style).pack(padx=10, pady=(10,5))
            popup_window_right_click.after(100, lambda: popup_window_right_click.focus_force())
            popup_window_right_click.bind('<FocusOut>', lambda e: popup_window_right_click.destroy())
        
        # Modern card-style background
        self.popup_report_visits.configure(fg_color="#f4f7fa")
        self.popup_report_visits.grid_columnconfigure(0, weight=1)
        self.popup_report_visits.grid_rowconfigure(0, minsize=100, weight=0)
        self.popup_report_visits.grid_rowconfigure(1, minsize=80, weight=0)
        self.popup_report_visits.grid_rowconfigure(2, weight=1)
        self.popup_report_visits.grid_rowconfigure(3, minsize=80, weight=0)

        # Header Frame
        header_frame = ctk.CTkFrame(self.popup_report_visits, fg_color="#ffffff", corner_radius=18, border_width=2, border_color="#e0e6ed", height=100)
        header_frame.grid(row=0, column=0, sticky="nsew", padx=32, pady=(24, 8))
        header_frame.grid_columnconfigure(0, weight=1)
        date_now = datetime.now().strftime("%d/%m/%Y")
        label_content = ctk.CTkLabel(header_frame, text=f'รายงานการเยี่ยม ประจำวันที่ {date_now}', font=('TH SarabunPSK', 36, 'bold'), text_color="#2d3a4b", fg_color="#ffffff")
        label_content.grid(row=0, column=0, sticky="nsew", pady=10,padx = 10)

        # Filter Frame
        filter_frame = ctk.CTkFrame(self.popup_report_visits, fg_color="#f8fbff", corner_radius=18, border_width=2, border_color="#e0e6ed", height=80)
        filter_frame.grid(row=1, column=0, sticky="nsew", padx=32, pady=(0, 8))
        # Add two empty columns left and right for centering
        filter_frame.grid_columnconfigure(0, weight=1)
        filter_frame.grid_columnconfigure(1, weight=0)
        filter_frame.grid_columnconfigure(2, weight=0)
        filter_frame.grid_columnconfigure(3, weight=0)
        filter_frame.grid_columnconfigure(4, weight=0)
        filter_frame.grid_columnconfigure(5, weight=0)
        filter_frame.grid_columnconfigure(6, weight=0)
        filter_frame.grid_columnconfigure(7, weight=1)

        current_year = datetime.now().year
        years = [str(current_year - 1), str(current_year), str(current_year + 1)]
        months_th = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
                    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
        month_numbers = [f"{i+1:02d}" for i in range(12)]
        month_dict = dict(zip(months_th, month_numbers))
        days_in_month = [f"{i:02d}" for i in range(1, 32)]

        year_var = ctk.StringVar(value=str(current_year))
        month_var = ctk.StringVar(value=months_th[datetime.now().month - 1])
        day_var = ctk.StringVar(value=f"{datetime.now().day:02d}")

        # Place widgets in columns 1-6 for centering
        label_select_round = ctk.CTkLabel(filter_frame, text='เลือกรอบเยี่ยม', font=('TH SarabunPSK', 28, 'bold'), text_color="#2d3a4b")
        label_select_round.grid(row=0, column=1, sticky='e', padx=(10, 5), pady=20)
        combo_year = ctk.CTkComboBox(filter_frame, values=years, variable=year_var, width=80, font=('TH SarabunPSK', 18), dropdown_font=('TH SarabunPSK', 18),
            fg_color='#ffffff', button_color='#4f8cff', text_color='#222', border_color='#b3d1ff')
        combo_month = ctk.CTkComboBox(filter_frame, values=months_th, variable=month_var, width=120, font=('TH SarabunPSK', 18), dropdown_font=('TH SarabunPSK', 18),
            fg_color='#ffffff', button_color='#4f8cff', text_color='#222', border_color='#b3d1ff')
        combo_day = ctk.CTkComboBox(filter_frame, values=days_in_month, variable=day_var, width=60, font=('TH SarabunPSK', 18), dropdown_font=('TH SarabunPSK', 18),
            fg_color='#ffffff', button_color='#4f8cff', text_color='#222', border_color='#b3d1ff')
        combo_year.grid(row=0, column=2, padx=5, pady=20)
        combo_month.grid(row=0, column=3, padx=5, pady=20)
        combo_day.grid(row=0, column=4, padx=5, pady=20)
        combo_round = ctk.CTkOptionMenu(filter_frame, values=['09:30:00','10:00:00','10:30:00','11:00:00','12:00:00','13:15:00','13:45:00','14:15:00'], font=('TH SarabunPSK', 18), dropdown_font=('TH SarabunPSK', 18),
            fg_color='#ffffff', button_color='#4f8cff', text_color='#222')
        combo_round.grid(row=0, column=5, sticky='ew', padx=20, pady=20)
        button = ctk.CTkButton(filter_frame, text='ค้นหา', font=('TH SarabunPSK', 18), command=lambda:get_visits(), fg_color="#4f8cff", hover_color="#2d3a4b", text_color="#fff", corner_radius=12)
        button.grid(row=0, column=6, sticky='w', padx=(10, 10), pady=20)
        search_name = ctk.CTkEntry(filter_frame, placeholder_text='ค้นหาชื่อผู้ต้องขัง', font=('TH SarabunPSK', 18), width=200, fg_color='#ffffff', border_color='#b3d1ff')
        search_name.grid(row=0, column=7, sticky='ew', padx=(10, 10), pady=20)

        # Table Frame
        table_frame = ctk.CTkFrame(self.popup_report_visits, fg_color="#ffffff", corner_radius=18, border_width=2, border_color="#e0e6ed")
        table_frame.grid(row=2, column=0, sticky="nsew", padx=32, pady=(0, 8))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # Treeview style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview',
            font =('TH SarabunPSK', 16),
            rowheight = 38,
            background="#f8fbff",
            fieldbackground="#f8fbff",
            bordercolor="#e0e6ed",
            borderwidth=1
        )
        style.configure('Treeview.Heading',
            font = ('TH SarabunPSK', 18, 'bold'),
            background="#4f8cff",
            foreground="#ffffff",
            borderwidth=2
        )
        style.map('Treeview', background=[('selected', '#b3d1ff')])

        tree_container = table_frame
        tree = ttk.Treeview(
            tree_container,
            columns=(
                'visit_id',
                'time_stamp',
                'date_visit',
                'time_visit',
                'prisoner_id',
                'dan',
                'relation_id_1',
                'relation_id_2',
                'relation_id_3',
                'relation_id_4',
                'relation_id_5',
                'channel'
            ),
            show='headings',
            height=12,
            style='Treeview'
        )
        tree.heading('visit_id',text='ID')
        tree.heading('time_stamp',text='Time Stamp')
        tree.heading('date_visit',text='วันที่จอง')
        tree.heading('time_visit',text='เวลาเยี่ยม')
        tree.heading('prisoner_id',text='ชื่อ')
        tree.heading('dan',text='แดน')
        tree.heading('relation_id_1',text='ญาติคนที่ 1')
        tree.heading('relation_id_2',text='ญาติคนที่ 2')
        tree.heading('relation_id_3',text='ญาติคนที่ 3')
        tree.heading('relation_id_4',text='ญาติคนที่ 4')
        tree.heading('relation_id_5',text='ญาติคนที่ 5')
        tree.heading('channel',text='ช่อง')

        tree.column('visit_id',width=0,stretch=False)
        tree.column('time_stamp', anchor='center')
        tree.column('date_visit', anchor='center')
        tree.column('time_visit', anchor='center')
        tree.column('prisoner_id', anchor='center')
        tree.column('dan', anchor='center')
        tree.column('relation_id_1', anchor='center')
        tree.column('relation_id_2', anchor='center')
        tree.column('relation_id_3', anchor='center')
        tree.column('relation_id_4', anchor='center')
        tree.column('relation_id_5', anchor='center')
        tree.column('channel',anchor='center')

        scrollbar = ttk.Scrollbar(tree_container, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        # scrollbar.grid(row=0, column=1, sticky='ns', pady=6)
        # tree.grid(row=0, column=0, sticky='new', padx=(0, 8), pady=6)
        
        # คลิกหัวคอลัมน์เพื่อเรียง/สลับทิศทางได้
        def _sort_tree_by(col, reverse=False):
            data = [(iid, tree.set(iid, col)) for iid in tree.get_children('')]
            def key_fn(v):
                return int(v) if str(v).isdigit() else float('inf')
            data.sort(key=lambda t: key_fn(t[1]), reverse=reverse)
            for idx, (iid, _) in enumerate(data):
                tree.move(iid, '', idx)
            tree.heading(col, command=lambda: _sort_tree_by(col, not reverse))

        tree.heading('channel', command=lambda: _sort_tree_by('channel', False))
        # กำหนดความกว้าง column
        column_ratios = {
            'time_stamp' : 0.11,
            'date_visit' : 0.07,
            'time_visit' : 0.07,
            'prisoner_id' : 0.12,
            'dan' : 0.03,
            'relation_id_1' : 0.11,
            'relation_id_2' : 0.11,
            'relation_id_3' : 0.11,
            'relation_id_4' : 0.11,
            'relation_id_5' : 0.11,
            'channel':0.03
        }
        search_name.bind('<Return>', lambda e: get_visits(search_name.get()))
        tree_container.bind('<Configure>',lambda e: resize_tree_column())
        tree.bind('<Button-3>',on_right_click)
        popup_window_right_click = None
######################################################################################### 
## รายงานเยี่ยมประจำเดือน
#########################################################################################
    def month_report_visits(self):

        def resize_tree_column():
            tree_container.update_idletasks()
            total_width = tree_container.winfo_width()
            # กำหนด anchor แต่ละคอลัมน์
            column_anchors = {
                'time_stamp': 'center',
                'date_visit': 'center', 
                'time_visit': 'center',
                'prisoner_id': 'w',
                'relation_id_1': 'w',
                'relation_id_2': 'w',
                'relation_id_3': 'w',
                'relation_id_4': 'w',
                'relation_id_5': 'w',
                'channel': 'center'
            }
            for col, ratio in column_ratios.items():
                anchor_type = column_anchors.get(col, 'w')  # default เป็น 'w'
                tree.column(col, width=int(total_width * ratio), anchor=anchor_type)

        def print_table():
            try:
                # สร้าง pdf
                temp_pdf = tempfile.mktemp(".pdf")
                c = canvas.Canvas(temp_pdf, pagesize=landscape(A4))
                width, height = landscape(A4)
                
                # ฟรอน และ ระยะห่าง
                c.setFont("TH SarabunPSK", 18)
                c.drawCentredString(width / 2, height - 1.5 * cm, f"รายงานการเยี่ยมรายเดือน เดือน {month_var.get()} ปี {year_var.get()}")
                c.setFont("TH SarabunPSK", 11)
                
                # หัวตารางและความกว้าง
                columns = tree["columns"]
                headers = [tree.heading(col)["text"] for col in columns if col != 'visit_id']
                
                # ปรับขนาด column ให้พอดีกับหน้ากระดาษ
                available_width = width - 2*cm  # หักขอบซ้าย-ขวา
                num_columns = len(headers)
                
                # กำหนดความกว้างแต่ละ column ตามเนื้อหา
                col_widths = []
                if num_columns == 10:  # จำนวน column ที่แสดง (ไม่รวม visit_id)
                    col_widths = [
                        available_width * 0.10,  # Time Stamp
                        available_width * 0.07,  # วันที่จอง
                        available_width * 0.07,  # เวลาเยี่ยม
                        available_width * 0.12,  # ชื่อผู้ต้องขัง
                        available_width * 0.12,  # ญาติคนที่ 1
                        available_width * 0.12,  # ญาติคนที่ 2
                        available_width * 0.12,  # ญาติคนที่ 3
                        available_width * 0.12,  # ญาติคนที่ 4
                        available_width * 0.11,  # ญาติคนที่ 5
                        available_width * 0.05,  # ช่อง
                    ]
                else:
                    # ถ้าจำนวน column ไม่ใช่ 10 ให้แบ่งเท่า ๆ กัน
                    col_widths = [available_width / num_columns] * num_columns
                
                # ตำแหน่งเริ่ม
                start_x = 1*cm
                start_y = height - 3 * cm
                row_height = 0.8*cm
                
                # วาดหัวตาราง
                y = start_y
                x = start_x
                for i, header in enumerate(headers):
                    c.setFillColorRGB(0.31, 0.55, 0.80)  # blue header
                    c.rect(x, y, col_widths[i], row_height, stroke=1, fill=1)
                    c.setFillColorRGB(1, 1, 1)
                    c.drawString(x+0.2*cm, y+0.3*cm, header)
                    x += col_widths[i]
                    
                # วาดข้อมูล
                y -= row_height
                for child_id in tree.get_children():
                    x = start_x
                    values = tree.item(child_id, "values")
                    for i, value in enumerate(values[1:]):  # ข้าม visit_id
                        c.setFillColorRGB(0.97, 0.98, 1) if y % 2 == 0 else c.setFillColorRGB(1, 1, 1)
                        c.rect(x, y, col_widths[i], row_height, stroke=1, fill=1)
                        c.setFillColorRGB(0, 0, 0)
                        text = str(value)
                        
                        # ตัดข้อความถ้ายาวเกินไป
                        max_width = col_widths[i] - 0.4*cm
                        text_width = c.stringWidth(text, "TH SarabunPSK", 11)
                        if text_width > max_width:
                            # ตัดข้อความและเพิ่ม ...
                            while text_width > max_width and len(text) > 3:
                                text = text[:-1]
                                text_width = c.stringWidth(text + "...", "TH SarabunPSK", 11)
                            text = text + "..."
                        
                        # จัดตำแหน่งข้อความ
                        if text.isdigit():
                            # จัดขวาสำหรับตัวเลข
                            text_width = c.stringWidth(text, "TH SarabunPSK", 11)
                            c.drawString(x+col_widths[i]-text_width-0.2*cm, y+0.3*cm, text)
                        else:
                            # จัดซ้ายสำหรับข้อความ
                            c.drawString(x+0.2*cm, y+0.3*cm, text)
                        x += col_widths[i]
                    y -= row_height
                    
                    # ตรวจสอบถ้าใกล้หมดหน้า ให้สร้างหน้าใหม่
                    if y < 2*cm:
                        c.showPage()
                        c.setFont("TH SarabunPSK", 11)
                        y = height - 2*cm
                
                c.save()
                os.startfile(temp_pdf)
                messagebox.showinfo('กำลังพิมพ์', 'สั่งพิมพ์เรียบร้อย')
                time.sleep(2)
                try:
                    os.remove(temp_pdf)
                except Exception:
                    pass
            except Exception as e:
                messagebox.showerror('ข้อผิดพลาด', f'ไม่สามารถพิมพ์ได้ :\n{e}')

        def get_visits():
            year = year_var.get()
            month = month_dict[month_var.get()]
            # ค้นหาข้อมูลทั้งเดือน
            data = [year, month]
            result = self.db.get_visits_by_month(data)
            print(f'data on get visits by month = {result}')

            # ล้างข้อมูลเดิมในตาราง
            for row_id in tree.get_children():
                tree.delete(row_id)

            # เตรียมคำค้นหาชื่อ (column ชื่อ อยู่ index 4)
            try:
                search_term = entry_search_name.get().strip().lower()
            except Exception:
                search_term = ""

            # ตรวจสอบและกรองข้อมูล
            if result and isinstance(result, (list, tuple)):
                filtered = []
                if search_term:
                    for r in result:
                        name_val = None
                        try:
                            name_val = r[4]
                        except Exception:
                            name_val = None
                        if name_val is not None and search_term in str(name_val).lower():
                            filtered.append(r)
                else:
                    filtered = list(result)

                if filtered:
                    for r in filtered:
                        # แทนที่ค่า None ด้วย "-"
                        processed_row = ["-" if v is None else v for v in r]
                        tree.insert('', 'end', values=processed_row)
                else:
                    # ไม่พบข้อมูลหลังกรอง
                    tree.insert('', 'end', values=('ไม่พบข้อมูล', '', '', '', '', '', '', '', '', '', ''))
            else:
                print("No data found or error occurred")
                # แสดงข้อความว่าไม่พบข้อมูล
                tree.insert('', 'end', values=('ไม่พบข้อมูล', '', '', '', '', '', '', '', '', '', ''))

            tree_container.grid(row=2, column=0, sticky='nsew')
            tree.grid(row=0, column=0, sticky='new', padx=6, pady=(8, 0))
            # ปุ่มพิมพ์แบบลอยขวา
            button_print = ctk.CTkButton(table_frame, text='พิมพ์', font=('TH SarabunPSK', 20, 'bold'), fg_color="#4f8cff", hover_color="#2d3a4b", text_color="#fff", corner_radius=12, command=lambda: print_table())
            button_print.grid(row=1, column=0, padx=16, pady=(8, 8))


        # Modern card-style background
        self.popup_report_visit_on_month.configure(fg_color="#f4f7fa")
        self.popup_report_visit_on_month.grid_columnconfigure(0, weight=1)
        self.popup_report_visit_on_month.grid_rowconfigure(0, minsize=100, weight=0)
        self.popup_report_visit_on_month.grid_rowconfigure(1, minsize=80, weight=0)
        self.popup_report_visit_on_month.grid_rowconfigure(2, weight=1)
        self.popup_report_visit_on_month.grid_rowconfigure(3, minsize=80, weight=0)

        # Header Frame
        header_frame = ctk.CTkFrame(self.popup_report_visit_on_month, fg_color="#ffffff", corner_radius=18, border_width=2, border_color="#e0e6ed", height=100)
        header_frame.grid(row=0, column=0, sticky="nsew", padx=32, pady=(24, 8))
        header_frame.grid_columnconfigure(0, weight=1)
        current_month = datetime.now().strftime("%m/%Y")
        label_content = ctk.CTkLabel(header_frame, text=f'รายงานการเยี่ยมรายเดือน ประจำเดือน {current_month}', font=('TH SarabunPSK', 36, 'bold'), text_color="#2d3a4b", fg_color="#ffffff")
        label_content.grid(row=0, column=0, sticky="nsew", pady=10, padx=10)

        # Filter Frame
        filter_frame = ctk.CTkFrame(self.popup_report_visit_on_month, fg_color="#f8fbff", corner_radius=18, border_width=2, border_color="#e0e6ed", height=80)
        filter_frame.grid(row=1, column=0, sticky="nsew", padx=32, pady=(0, 8))
        # Add columns for centering
        filter_frame.grid_columnconfigure(0, weight=1)
        filter_frame.grid_columnconfigure(1, weight=0)
        filter_frame.grid_columnconfigure(2, weight=0)
        filter_frame.grid_columnconfigure(3, weight=0)
        filter_frame.grid_columnconfigure(4, weight=1)
        filter_frame.grid_columnconfigure(5, weight=0)

        current_year = datetime.now().year
        years = [str(current_year - 1), str(current_year), str(current_year + 1)]
        months_th = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
                    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
        month_numbers = [f"{i+1:02d}" for i in range(12)]
        month_dict = dict(zip(months_th, month_numbers))

        year_var = ctk.StringVar(value=str(current_year))
        month_var = ctk.StringVar(value=months_th[datetime.now().month - 1])

        # Place widgets in columns for centering
        label_select_month = ctk.CTkLabel(filter_frame, text='เลือกเดือนและปี', font=('TH SarabunPSK', 28, 'bold'), text_color="#2d3a4b")
        label_select_month.grid(row=0, column=1, sticky='e', padx=(10, 5), pady=20)
        combo_year = ctk.CTkComboBox(filter_frame, values=years, variable=year_var, width=100, font=('TH SarabunPSK', 18), dropdown_font=('TH SarabunPSK', 18),
            fg_color='#ffffff', button_color='#4f8cff', text_color='#222', border_color='#b3d1ff')
        combo_month = ctk.CTkComboBox(filter_frame, values=months_th, variable=month_var, width=140, font=('TH SarabunPSK', 18), dropdown_font=('TH SarabunPSK', 18),
            fg_color='#ffffff', button_color='#4f8cff', text_color='#222', border_color='#b3d1ff')
        combo_year.grid(row=0, column=2, padx=5, pady=20)
        combo_month.grid(row=0, column=3, padx=5, pady=20)
        button = ctk.CTkButton(filter_frame, text='ค้นหา', font=('TH SarabunPSK', 18), command=lambda:get_visits(), fg_color="#4f8cff", hover_color="#2d3a4b", text_color="#fff", corner_radius=12)
        button.grid(row=0, column=4, sticky='w', padx=(10, 10), pady=20)
        entry_search_name = ctk.CTkEntry(filter_frame, placeholder_text='ค้นหาชื่อผู้ต้องขัง', font=('TH SarabunPSK', 18), width=200, fg_color="#ffffff", text_color="#222", border_color="#b3d1ff")
        entry_search_name.grid(row=0, column=5, sticky='ew', padx=(10, 10), pady=20)
        # พิมพ์แล้วค้นหาอัตโนมัติ
        entry_search_name.bind('<KeyRelease>', lambda e: get_visits())

        # แสดงข้อมูลเริ่มต้นของเดือนปัจจุบัน
        try:
            get_visits()
        except Exception as _e:
            print('initial get_visits error: ', _e)

        # Table Frame
        table_frame = ctk.CTkFrame(self.popup_report_visit_on_month, fg_color="#ffffff", corner_radius=18, border_width=2, border_color="#e0e6ed")
        table_frame.grid(row=2, column=0, sticky="nsew", padx=32, pady=(0, 8))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # Treeview style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview',
            font =('TH SarabunPSK', 18),
            rowheight = 38,
            background="#f8fbff",
            fieldbackground="#f8fbff",
            bordercolor="#e0e6ed",
            borderwidth=1
        )
        style.configure('Treeview.Heading',
            font = ('TH SarabunPSK', 20, 'bold'),
            background="#4f8cff",
            foreground="#ffffff",
            borderwidth=2
        )
        style.map('Treeview', background=[('selected', '#b3d1ff')])

        tree_container = table_frame
        tree = ttk.Treeview(
            tree_container,
            columns=(
                'visit_id',
                'time_stamp',
                'date_visit',
                'time_visit',
                'prisoner_id',
                'relation_id_1',
                'relation_id_2',
                'relation_id_3',
                'relation_id_4',
                'relation_id_5',
                'channel'
            ),
            show='headings',
            height=12,
            style='Treeview'
        )
        tree.heading('visit_id',text='ID')
        tree.heading('time_stamp',text='Time Stamp')
        tree.heading('date_visit',text='วันที่จอง')
        tree.heading('time_visit',text='เวลาเยี่ยม')
        tree.heading('prisoner_id',text='ชื่อ')
        tree.heading('relation_id_1',text='ญาติคนที่ 1')
        tree.heading('relation_id_2',text='ญาติคนที่ 2')
        tree.heading('relation_id_3',text='ญาติคนที่ 3')
        tree.heading('relation_id_4',text='ญาติคนที่ 4')
        tree.heading('relation_id_5',text='ญาติคนที่ 5')
        tree.heading('channel',text='ช่อง')

        tree.column('visit_id',width=0,stretch=False)
        tree.column('time_stamp', anchor='center')
        tree.column('date_visit', anchor='center')
        tree.column('time_visit', anchor='center')
        tree.column('prisoner_id', anchor='w')
        tree.column('relation_id_1', anchor='w')
        tree.column('relation_id_2', anchor='w')
        tree.column('relation_id_3', anchor='w')
        tree.column('relation_id_4', anchor='w')
        tree.column('relation_id_5', anchor='w')
        tree.column('channel',anchor='w')

        scrollbar = ttk.Scrollbar(tree_container, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # กำหนดความกว้าง column
        column_ratios = {
            'time_stamp' : 0.11,
            'date_visit' : 0.08,
            'time_visit' : 0.08,
            'prisoner_id' : 0.12,
            'relation_id_1' : 0.11,
            'relation_id_2' : 0.11,
            'relation_id_3' : 0.11,
            'relation_id_4' : 0.11,
            'relation_id_5' : 0.11,
            'channel':0.06
        }
        tree_container.bind('<Configure>',lambda e: resize_tree_column())
        # tree.bind('<Button-3>',on_right_click)
        popup_window_right_click = None
        pass
##############################################################################################################################################################################
    # function แสดงหน้าตามปุ่มกดจากหน้า Menu Frame
##############################################################################################################################################################################

    def show_page(self,page_name):
        print('showpage + ', page_name)
        for widgets in self.winfo_children():
            widgets.pack_forget()
        if page_name == 'ลงทะเบียนผู้ต้องขัง':
            self.register_frame.pack(fill='both',expand = True)
            self.register_prisoner()
        elif page_name == 'ค้นหาผู้ต้องขัง':
            self.showdata_frame.pack(fill='both',expand = True)
            self.search_one_prisoner()
        elif page_name == 'ย้ายแดน,ปรับชั้น':
            self.move_dan_and_adjust_level_frame.pack(fill='both',expand=True)
            self.move_and_adjust()
        elif page_name == 'ผู้ต้องขังทั้งหมด':
            print(page_name)
            self.show_all_prisoner_frame.pack(fill='both',expand = True)
            self.search_all_prisoner()
        elif page_name == 'จองเยี่ยม':
            print(page_name)
            self.reserve_visit_frame.pack(fill='both',expand = True)
            self.reserve_to_visit()
        elif page_name == 'ลงทะเบียนลายนิ้วมือ':
            print(page_name)
            self.fingerprint_frame.pack(fill='both',expand = True)
            self.register_fingerprint()
        elif page_name == 'รายงาน':
            print(page_name)
            self.popup_report_visits.pack(fill='both',expand = True)
            self.report_visits()
        elif page_name == 'ญาติทั้งหมด':
            print(page_name)
            self.show_all_relative_frame.pack(fill='both',expand = True)
            self.search_all_relatives()
        elif page_name == 'จองเยี่ยมญาติด้วยเลขบัตรประชาชน':
            print(page_name)
            self.reserve_visit_by_national_id_frame.pack(fill='both',expand = True)
            self.reserve_visit_by_national_id()
        elif page_name == 'รายงานประจำเดือน':
            self.popup_report_visit_on_month.pack(fill='both',expand = True)
            self.month_report_visits()

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
                # ปิด connection เดิมก่อน
                try:
                    self.db.close()
                except:
                    pass
                # สร้าง instance ใหม่เพื่อโหลด config ล่าสุด
                from manage.database import SQLiteDB
                self.db = SQLiteDB()
                print("อัปเดต database connection ใน MainFrame สำเร็จ")
            
            print("รีเฟรชข้อมูลใน MainFrame เสร็จสิ้น")
            
        except Exception as e:
            print(f"Error in MainFrame refresh_data: {e}")

    def update_database_path(self, new_path):
        """อัปเดต path ฐานข้อมูลใหม่"""
        try:
            print(f"อัปเดต database path ใน MainFrame: {new_path}")
            
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
            
            print(f"Database path อัปเดตเป็น: {new_path}")
            
        except Exception as e:
            print(f"Error updating database path in MainFrame: {e}")