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

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape,A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import os
import tempfile

pdfmetrics.registerFont(TTFont("TH SarabunPSK", "THSarabun.ttf"))

class MORING_ROUNDS:
    """คลาสสำหรับจัดการข้อมูลรอบเช้า"""
    def __init__(self):
        self.rounds = [
            ('รอบที่ 1 เวลา 09.30 - 09.45', '09:30:00', '09:15:00'),
            ('รอบที่ 2 เวลา 10.00 - 10.15', '10:00:00', '09:45:00'),
            ('รอบที่ 3 เวลา 10.30 - 10.45', '10:30:00', '10:15:00'),
            ('รอบที่ 4 เวลา 11.00 - 11.15', '11:00:00', '10:15:00'),
        ]

    def get_available_rounds(self, now, late_time):
        """คืนค่ารอบที่ยังสามารถเลือกได้ตามเวลาปัจจุบัน"""
        from datetime import datetime
        available = []
        for text, start, close in self.rounds:
            close_time = datetime.strptime(close, "%H:%M:%S").time()
            if now < close_time or now > late_time:
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

    def get_available_rounds(self, now, late_time):
        """คืนค่ารอบที่ยังสามารถเลือกได้ตามเวลาปัจจุบัน"""
        from datetime import datetime
        available = []
        for text, start, close in self.rounds:
            close_time = datetime.strptime(close, "%H:%M:%S").time()
            if now < close_time or now > late_time:
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
        frame_border = ctk.CTkFrame(self, corner_radius=5, fg_color='black')
        frame_border.pack(fill='both', expand=True, padx=2, pady=2)
        frame_inner = ctk.CTkFrame(frame_border, corner_radius=3)
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
        super().__init__(parent,bg_color='#D7F197')

        self.grid(row=0,column=1,sticky='nsew')
        self.db = SQLiteDB()
        self.zkfp2 = ZKFP2()
        self.thai_id_reader = ThaiIDReader()

        # สร้าง Frame ลงทะเบียนผู้ต้องขัง #
        self.register_frame = ctk.CTkFrame(self)

        # สร้าง Frame เมนูค้นหาผู้ต้องขังเพือจัดการญาติ #
        self.showdata_frame = ctk.CTkFrame(self)

        # สร้าง Frame เมนู ย้ายแดน และปรับชั้น #
        self.move_dan_and_adjust_level_frame = ctk.CTkFrame(self)

        # สร้าง Frame แสดงข้อมูลผู้ต้องขังทั้งหมดเป็นตาราง #
        self.show_all_prisoner_frame = ctk.CTkFrame(self)

        # สร้าง Frame แสดงข้อมูลญาติทั้งหมดเป็นตาราง 
        self.show_all_relative_frame = ctk.CTkFrame(self)

        # สร้าง Frame สำหรับรายงานประวัติการเยี่ยมญาติ
        self.popup_report_visits = ctk.CTkFrame(self) 

        self.reserve_visit_by_national_id_frame = ctk.CTkFrame(self)  # สำหรับจองเยี่ยมญาติด้วยหมายเลขบัตรประชาชน

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
        self.register_frame.grid_columnconfigure((0,1),weight=1,uniform="register_frame")
        self.register_frame.grid_rowconfigure((0,1,2,3,4,5,6,7,8,9),weight=1,uniform="register_frame")
        
        # progressbar = ctk.CTkProgressBar(self.register_frame,mode='indeterminate')

        regis_label_content = ctk.CTkLabel(self.register_frame,text='ลงทะเบียนผู้ต้องขัง',font=('TH SarabunPSK',40,'bold'))
        regis_label_content.grid(row = 0,column = 0,columnspan = 2,sticky = 'nsew' , pady = 10)

        regis_label_id = ctk.CTkLabel(self.register_frame,text='รหัสประจำตัว : ',font=('TH SarabunPSK',18,'bold'),width=200,anchor='e')
        regis_label_id.grid(row = 1,column = 0,sticky = 'e',padx = 5)
        regis_entry_id = ctk.CTkEntry(self.register_frame,font=('TH SarabunPSK',18),width=200,validate='key',validatecommand = (self.vcmd,'%P'))
        regis_entry_id.grid(row = 1,column = 1,sticky = 'w',padx = 5)

        regis_label_sex = ctk.CTkLabel(self.register_frame,text='เพศ : ',font=('TH SarabunPSK',18,'bold'))
        regis_label_sex.grid(row = 2,column = 0,sticky = 'e',padx = 5)
        regis_combo_sex = ctk.CTkOptionMenu(self.register_frame,values=['ชาย','หญิง'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
        regis_combo_sex.grid(row = 2,column = 1,sticky = 'w',padx = 5)
        
        regis_label_name = ctk.CTkLabel(self.register_frame,text='ชื่อ : ',font=('TH SarabunPSK',18,'bold'))
        regis_label_name.grid(row = 3 ,column = 0,sticky = 'e',padx = 5)
        regis_entry_name = ctk.CTkEntry(self.register_frame,font=('TH SarabunPSK',18),width=200)
        regis_entry_name.grid(row = 3,column = 1,sticky = 'w',padx = 5)

        regis_label_lname = ctk.CTkLabel(self.register_frame,text='นามสกุล : ',font=('TH SarabunPSK',18,'bold'))
        regis_label_lname.grid(row = 4,column = 0,sticky = 'e',padx = 5)
        regis_entry_lname = ctk.CTkEntry(self.register_frame,font=('TH SarabunPSK',18),width=200)
        regis_entry_lname.grid(row = 4,column = 1,sticky = 'w',padx = 5)

        regis_label_lawsuit = ctk.CTkLabel(self.register_frame,text='คดี : ',font=('TH SarabunPSK',18,'bold'))
        regis_label_lawsuit.grid(row = 5 ,column = 0,sticky = 'e',padx = 5)
        regis_entry_lawsuit = ctk.CTkTextbox(self.register_frame,font=('TH SarabunPSK',18),width=200,height=60)
        regis_entry_lawsuit.grid(row = 5,column = 1 ,sticky = 'w',padx = 5)

        regis_label_level = ctk.CTkLabel(self.register_frame,text='ชั้น : ',font=('TH SarabunPSK',18,'bold'))
        regis_label_level.grid(row = 6 ,column = 0,sticky = 'e',padx = 5)
        regis_combo_level = ctk.CTkOptionMenu(self.register_frame,values=['ระหว่างพิจารณาคดี','เยี่ยม','ดีมาก','ดี','กลาง','ปรับปรุง','ปรับปรุงมาก'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
        regis_combo_level.grid(row = 6 ,column = 1,sticky = 'w',padx = 5)

        regis_label_dan = ctk.CTkLabel(self.register_frame,text='แดน : ',font=('TH SarabunPSK',18,'bold'))
        regis_label_dan.grid(row = 7,column = 0,sticky = 'e',padx = 5)
        regis_combo_dan = ctk.CTkOptionMenu(self.register_frame,values=['1','2','3','4','5','6','7','รจช'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
        regis_combo_dan.grid(row = 7,column = 1,sticky = 'w',padx = 5)

        regis_label_type = ctk.CTkLabel(self.register_frame,text='สถานะ : ',font=('TH SarabunPSK',18,'bold'))
        regis_label_type.grid(row = 8,column = 0,sticky = 'e',padx = 5)
        regis_combo_type = ctk.CTkOptionMenu(self.register_frame,values=['ผู้ต้องขัง','ผู้ต้องกักขัง'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
        regis_combo_type.grid(row = 8,column = 1,sticky = 'w',padx = 5)

        regis_button_submit = ctk.CTkButton(self.register_frame,
                                           text='บันทึกข้อมูล',
                                           width=100,
                                           font=('TH SarabunPSK',18,'bold'),
                                           command=lambda:save_data_to_db())
        regis_button_submit.grid(row = 9,column = 0,sticky = 'e',padx = 5)
        regis_button_clear = ctk.CTkButton(self.register_frame,
                                          text='ล้างข้อมูล',
                                          width=100,
                                          font=('TH SarabunPSK',18,'bold'),
                                          command=lambda:clear_data())
        regis_button_clear.grid(row = 9,column = 1,sticky = 'w',padx = 5)

        self.register_frame.grid_columnconfigure((0,1),minsize=300)

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

                id_relative = ctk.StringVar()
                f_name_var = ctk.StringVar()
                l_name_var = ctk.StringVar()
                address_var = ctk.StringVar()
                tel_var = ctk.StringVar()
                frame_data_relative = ctk.CTkFrame(popup_register_relation)
                for i in range(7):
                    frame_data_relative.grid_rowconfigure(i,weight=1,uniform='popup')
                # ตั้งค่า column
                for i in range(4):
                    popup_register_relation.grid_columnconfigure(i,weight=1,uniform='popup')
                    frame_data_relative.grid_columnconfigure(i,weight=1,uniform='popup')
                popup_register_relation.grid_rowconfigure(3,weight=1,uniform='popup')

                popup_label_content =ctk.CTkLabel(popup_register_relation,text='ลงทะเบียนญาติ',font=('TH SarabunPSK',28,'bold'))
                popup_label_content.grid(row = 0,column =0,columnspan = 4,pady = 10)

                popup_label_prisoner_id = ctk.CTkLabel(popup_register_relation,text='รหัสประจำตัว : ',font=('TH SarabunPSK',18,'bold'))
                popup_label_prisoner_id.grid(row = 1,column = 0,padx= 5,sticky = 'e',pady = 5)
                
                popup_label_prisoner_id_form_search_one = ctk.CTkLabel(popup_register_relation,text=prisoner_id_in_search_one,font=('TH SarabunPSK',18,'bold'))
                popup_label_prisoner_id_form_search_one.grid(row = 1,column = 1,padx= 5,sticky = 'w',pady = 5)

                popup_label_prisoner_name = ctk.CTkLabel(popup_register_relation,text='ชื่อ : ',font=('TH SarabunPSK',18,'bold'))
                popup_label_prisoner_name.grid(row = 1,column = 2,padx= 5,sticky = 'e',pady = 5)

                popup_label_prisoner_name_form_search_one = ctk.CTkLabel(popup_register_relation,text=prisoner_name_in_search_one,font=('TH SarabunPSK',18,'bold'))
                popup_label_prisoner_name_form_search_one.grid(row = 1,column = 3,padx= 5,sticky = 'w',pady = 5)

                popup_label_id_relative = ctk.CTkLabel(popup_register_relation,text='หมายเลขบัตรประชาชน',font=('TH SarabunPSK',18,'bold'))
                popup_label_id_relative.grid(row = 2,column = 0,columnspan = 2,padx= 5,sticky = 'e',pady = 5)

                popup_entry_id_relative = ctk.CTkEntry(popup_register_relation,font=('TH SarabunPSK',18),textvariable=id_relative,validate='key',validatecommand = (self.vcmd,'%P'))
                popup_entry_id_relative.grid(row = 2,column = 2,padx= 5,sticky = 'w',pady = 5)

                popup_button_check_id = ctk.CTkButton(popup_register_relation,
                                                      text='ตรวจสอบ',
                                                      width=100,
                                                      font=('TH SarabunPSK',18,'bold'),
                                                      command=lambda:check_relative_id())
                popup_button_check_id.grid(row=2 ,column = 3,padx= 5,sticky = 'w',pady = 5)

                popup_label_title_relative = ctk.CTkLabel(frame_data_relative,text='คำนำหน้า : ',font=('TH SarabunPSK',18,'bold'))
                popup_label_title_relative.grid(row = 0,column = 0,columnspan = 2,sticky = 'e',padx = 5)

                popup_combo_title_relative = ctk.CTkOptionMenu(frame_data_relative,values=['นาย','นาง','นางสาว','เด็กหญิง','เด็กชาย'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
                popup_combo_title_relative.grid(row = 0,column = 2,columnspan = 2,sticky = 'w',padx = 5)

                popup_label_fname_relative = ctk.CTkLabel(frame_data_relative,text='ชื่อ : ',font=('TH SarabunPSK',18,'bold'))
                popup_label_fname_relative.grid(row = 1,column = 0,columnspan = 2,padx= 5,sticky = 'e')

                popup_entry_fname_relative = ctk.CTkEntry(frame_data_relative,font=('TH SarabunPSK',18),textvariable=f_name_var)
                popup_entry_fname_relative.grid(row = 1,column = 2,columnspan = 2,padx= 5,sticky = 'w')

                popup_label_lname_relative = ctk.CTkLabel(frame_data_relative,text='นามสกุล : ',font=('TH SarabunPSK',18,'bold'))
                popup_label_lname_relative.grid(row = 2,column = 0,columnspan = 2,padx= 2,sticky = 'e')

                popup_entry_lname_relative = ctk.CTkEntry(frame_data_relative,font=('TH SarabunPSK',18),textvariable=l_name_var,)
                popup_entry_lname_relative.grid(row = 2,column = 2,columnspan = 2,padx= 5,sticky = 'w')

                popup_label_address_relative = ctk.CTkLabel(frame_data_relative,text='ที่อยู่ : ',font=('TH SarabunPSK',18,'bold'))
                popup_label_address_relative.grid(row = 3,column = 0,columnspan = 2,padx= 5,sticky = 'e')

                popup_entry_address_relative = ctk.CTkEntry(frame_data_relative,font=('TH SarabunPSK',18),textvariable=address_var)
                popup_entry_address_relative.grid(row = 3,column = 2,columnspan = 2,padx= 5,sticky = 'w')

                popup_label_tel_relative = ctk.CTkLabel(frame_data_relative,text='เบอร์โทร : ',font=('TH SarabunPSK',18,'bold'))
                popup_label_tel_relative.grid(row = 4,column = 0,columnspan = 2,padx= 5,sticky = 'e')

                popup_entry_tel_relative = ctk.CTkEntry(frame_data_relative,font=('TH SarabunPSK',18),textvariable=tel_var,validate='key',validatecommand = (self.vcmd,'%P'))
                popup_entry_tel_relative.grid(row = 4,column = 2,columnspan = 2,padx= 5,sticky = 'w')

                popup_label_relation_relative = ctk.CTkLabel(frame_data_relative,text='ความสัมพันธ์ : ',font=('TH SarabunPSK',18,'bold'))
                popup_label_relation_relative.grid(row = 5,column = 0,columnspan = 2,padx= 5,sticky = 'e')
                popup_combo_relation_relative = ctk.CTkOptionMenu(frame_data_relative,values=['ปู่','ย่า','ตา','ยาย','ลุง','ป้า','พ่อ','แม่','น้า','พี่ชาย','พี่สาว','น้องชาย','น้องสาว','สามี','ภรรยา','ลูกสาว','ลูกชาย','อื่น ๆ'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
                popup_combo_relation_relative.grid(row = 5,column = 2,columnspan = 2,padx= 5,sticky = 'w')

                popup_button_submit = ctk.CTkButton(frame_data_relative,
                                                    text='บันทึกข้อมูล',
                                                    width=100,
                                                    font=('TH SarabunPSK',18,'bold'),
                                                    command=lambda:save_regis_relative_to_db()
                                                    )
                popup_button_cancel = ctk.CTkButton(frame_data_relative,
                                                    text='ยกเลิก',
                                                    width=100,
                                                    font=('TH SarabunPSK',18,'bold'),
                                                    fg_color='red',
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
            ctk.CTkLabel(popup_show_list,text=f'ข้อมูลญาติของ {prisoner_name_in_search_one}',font=('TH SarabunPSK',40,'bold')).grid(row = 0,column = 0,sticky = 'nsew')

            tree_container = ctk.CTkFrame(popup_show_list)
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

        showdata_label_content = ctk.CTkLabel(self.showdata_frame,text='ค้นหาผู้ต้องขัง',font=('TH SarabunPSK',40,'bold'))
        showdata_label_content.grid(row = 0,column = 0,columnspan = 2,sticky = 'nsew' , pady = 10)

        showdata_label_search = ctk.CTkLabel(self.showdata_frame,text='ระบุรหัสประจำตัวผู้ต้องขัง : ',font=('TH SarabunPSK',18,'bold'))
        showdata_label_search.grid(row = 1,column = 0,sticky = 'e',padx = 5)

        showdata_entry_search = ctk.CTkEntry(self.showdata_frame,textvariable=search_one_var,font=('TH SarabunPSK',18,'bold'),validate='key',validatecommand = (self.vcmd,'%P'))
        showdata_entry_search.grid(row = 1,column = 1,sticky = 'w',padx = 5)

        button_search = ctk.CTkButton(self.showdata_frame,
                                      text='ค้นหาข้อมูลผู้ต้องขัง',
                                      font=('TH SarabunPSK',18,'bold'),
                                      command=lambda:show_one_prisoner())
        button_search.grid(row = 2,column = 0,columnspan = 2)

        showdata_search_frame = ctk.CTkFrame(self.showdata_frame)
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
 

        search_frame = ctk.CTkFrame(self.move_dan_and_adjust_level_frame)

        label_content = ctk.CTkLabel(self.move_dan_and_adjust_level_frame,text='ย้ายแดน และ ปรับชั้น',font=('TH SarabunPSK',40,'bold'))
        label_content.grid(row = 0,column = 0,columnspan = 2,sticky = 'nsew' , pady = 10)

        label_search = ctk.CTkLabel(self.move_dan_and_adjust_level_frame,text='ระบุรหัสประจำตัวผู้ต้องขัง : ',font=('TH SarabunPSK',18,'bold'))
        label_search.grid(row = 1,column = 0,sticky = 'e',padx = 5,pady = 20)

        entry_search = ctk.CTkEntry(self.move_dan_and_adjust_level_frame,textvariable=search_one_var,font=('TH SarabunPSK',18,'bold'),validate='key',validatecommand = (self.vcmd,'%P'))
        entry_search.grid(row = 1,column = 1,sticky = 'w',padx = 5,pady = 20)

        button_search = ctk.CTkButton(self.move_dan_and_adjust_level_frame,
                                      text='ค้นหาข้อมูลผู้ต้องขัง',
                                      font=('TH SarabunPSK',18,'bold'),
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
        dan_data = ctk.CTkOptionMenu(search_frame,values=['1','2','3','4','5','6','7','รจช'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
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
                                                    command=lambda:update_level_and_dan()
                                                    )
        button_submit.grid(row = 9,column = 0,columnspan = 2,sticky = 'n',padx = 5)

        self.move_dan_and_adjust_level_frame.grid_columnconfigure((0,1),minsize=200)

##############################################################################################################################################################################
#   ค้นหาผู้ต้องขังทั้งหมด
##############################################################################################################################################################################
    def search_all_prisoner(self):

        def add_relative(prisoner_id, f_name, l_name):
            # ใช้ prisoner_id, f_name, l_name ที่ส่งมาจากการคลิกขวา
            print(f"เพิ่มญาติสำหรับผู้ต้องขัง: {prisoner_id} {f_name} {l_name}")
            # ที่นี่คุณสามารถใช้ข้อมูลนี้เพื่อแสดงหรือดำเนินการอื่น ๆ

            popup_register_relation = ctk.CTkToplevel(self)
            popup_register_relation.title('ลงทะเบียนญาติ')
            popup_register_relation.geometry('480x720+1+1')
            popup_register_relation.grab_set()

            id_relative = ctk.StringVar()
            f_name_var = ctk.StringVar()
            l_name_var = ctk.StringVar()
            address_var = ctk.StringVar()
            tel_var = ctk.StringVar()
            frame_data_relative = ctk.CTkFrame(popup_register_relation)
            for i in range(7):
                frame_data_relative.grid_rowconfigure(i,weight=1,uniform='popup')
            # ตั้งค่า column
            for i in range(4):
                popup_register_relation.grid_columnconfigure(i,weight=1,uniform='popup')
                frame_data_relative.grid_columnconfigure(i,weight=1,uniform='popup')
            popup_register_relation.grid_rowconfigure(3,weight=1,uniform='popup')

            popup_label_content =ctk.CTkLabel(popup_register_relation,text='ลงทะเบียนญาติ',font=('TH SarabunPSK',28,'bold'))
            popup_label_content.grid(row = 0,column =0,columnspan = 4,pady = 10)

            popup_label_prisoner_id = ctk.CTkLabel(popup_register_relation,text='รหัสประจำตัว : ',font=('TH SarabunPSK',18,'bold'))
            popup_label_prisoner_id.grid(row = 1,column = 0,padx= 5,sticky = 'e',pady = 5)
            
            popup_label_prisoner_id_form_search_one = ctk.CTkLabel(popup_register_relation,text=prisoner_id,font=('TH SarabunPSK',18,'bold'))
            popup_label_prisoner_id_form_search_one.grid(row = 1,column = 1,padx= 5,sticky = 'w',pady = 5)

            popup_label_prisoner_name = ctk.CTkLabel(popup_register_relation,text='ชื่อ : ',font=('TH SarabunPSK',18,'bold'))
            popup_label_prisoner_name.grid(row = 1,column = 2,padx= 5,sticky = 'e',pady = 5)

            popup_label_prisoner_name_form_search_one = ctk.CTkLabel(popup_register_relation,text=f'{f_name} {l_name}',font=('TH SarabunPSK',18,'bold'))
            popup_label_prisoner_name_form_search_one.grid(row = 1,column = 3,padx= 5,sticky = 'w',pady = 5)

            popup_label_id_relative = ctk.CTkLabel(popup_register_relation,text='หมายเลขบัตรประชาชน',font=('TH SarabunPSK',18,'bold'))
            popup_label_id_relative.grid(row = 2,column = 0,columnspan = 2,padx= 5,sticky = 'e',pady = 5)

            popup_entry_id_relative = ctk.CTkEntry(popup_register_relation,font=('TH SarabunPSK',18),textvariable=id_relative,validate='key',validatecommand = (self.vcmd,'%P'))
            popup_entry_id_relative.grid(row = 2,column = 2,padx= 5,sticky = 'w',pady = 5)

            popup_entry_id_relative.bind('<Return>', lambda event: check_relative_id())

            popup_button_check_id = ctk.CTkButton(popup_register_relation,
                                                    text='ตรวจสอบ',
                                                    width=100,
                                                    font=('TH SarabunPSK',18,'bold'),
                                                    command=lambda:check_relative_id()
                                                    )
            popup_button_check_id.grid(row=2 ,column = 3,padx= 5,sticky = 'w',pady = 5)

            popup_label_title_relative = ctk.CTkLabel(frame_data_relative,text='คำนำหน้า : ',font=('TH SarabunPSK',18,'bold'))
            popup_label_title_relative.grid(row = 0,column = 0,columnspan = 2,sticky = 'e',padx = 5)

            popup_combo_title_relative = ctk.CTkOptionMenu(frame_data_relative,values=['นาย','นาง','นางสาว','เด็กหญิง','เด็กชาย'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
            popup_combo_title_relative.grid(row = 0,column = 2,columnspan = 2,sticky = 'w',padx = 5)

            popup_label_fname_relative = ctk.CTkLabel(frame_data_relative,text='ชื่อ : ',font=('TH SarabunPSK',18,'bold'))
            popup_label_fname_relative.grid(row = 1,column = 0,columnspan = 2,padx= 5,sticky = 'e')

            popup_entry_fname_relative = ctk.CTkEntry(frame_data_relative,font=('TH SarabunPSK',18),textvariable=f_name_var)
            popup_entry_fname_relative.grid(row = 1,column = 2,columnspan = 2,padx= 5,sticky = 'w')

            popup_label_lname_relative = ctk.CTkLabel(frame_data_relative,text='นามสกุล : ',font=('TH SarabunPSK',18,'bold'))
            popup_label_lname_relative.grid(row = 2,column = 0,columnspan = 2,padx= 2,sticky = 'e')

            popup_entry_lname_relative = ctk.CTkEntry(frame_data_relative,font=('TH SarabunPSK',18),textvariable=l_name_var,)
            popup_entry_lname_relative.grid(row = 2,column = 2,columnspan = 2,padx= 5,sticky = 'w')

            popup_label_address_relative = ctk.CTkLabel(frame_data_relative,text='ที่อยู่ : ',font=('TH SarabunPSK',18,'bold'))
            popup_label_address_relative.grid(row = 3,column = 0,columnspan = 2,padx= 5,sticky = 'e')

            popup_entry_address_relative = ctk.CTkEntry(frame_data_relative,font=('TH SarabunPSK',18),textvariable=address_var)
            popup_entry_address_relative.grid(row = 3,column = 2,columnspan = 2,padx= 5,sticky = 'w')

            popup_label_tel_relative = ctk.CTkLabel(frame_data_relative,text='เบอร์โทร : ',font=('TH SarabunPSK',18,'bold'))
            popup_label_tel_relative.grid(row = 4,column = 0,columnspan = 2,padx= 5,sticky = 'e')

            popup_entry_tel_relative = ctk.CTkEntry(frame_data_relative,font=('TH SarabunPSK',18),textvariable=tel_var,validate='key',validatecommand = (self.vcmd,'%P'))
            popup_entry_tel_relative.grid(row = 4,column = 2,columnspan = 2,padx= 5,sticky = 'w')

            popup_label_relation_relative = ctk.CTkLabel(frame_data_relative,text='ความสัมพันธ์ : ',font=('TH SarabunPSK',18,'bold'))
            popup_label_relation_relative.grid(row = 5,column = 0,columnspan = 2,padx= 5,sticky = 'e')
            popup_combo_relation_relative = ctk.CTkOptionMenu(frame_data_relative,values=['ปู่','ย่า','ตา','ยาย','ลุง','ป้า','พ่อ','แม่','น้า','พี่ชาย','พี่สาว','น้องชาย','น้องสาว','สามี','ภรรยา','ลูกสาว','ลูกชาย','อื่น ๆ'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
            popup_combo_relation_relative.grid(row = 5,column = 2,columnspan = 2,padx= 5,sticky = 'w')

            popup_button_submit = ctk.CTkButton(frame_data_relative,
                                                text='บันทึกข้อมูล',
                                                width=100,
                                                font=('TH SarabunPSK',18,'bold'),
                                                command=lambda:save_regis_relative_to_db()
                                                )
            popup_button_cancel = ctk.CTkButton(frame_data_relative,
                                                text='ยกเลิก',
                                                width=100,
                                                font=('TH SarabunPSK',18,'bold'),
                                                fg_color='red',
                                                command=lambda:clear_popup_regis()
                                                )
            popup_button_submit.grid(row = 6,column = 0,padx = 5,columnspan = 2,sticky ='e' )
            popup_button_cancel.grid(row = 6,column = 2,padx = 5,columnspan = 2,sticky ='w' )

            

            def on_close():
                print('popup register ถูกปิด')
                popup_register_relation.destroy()

            def check_relative_id():
                try:
                    self.thai_id_reader.read_card()
                    info = self.thai_id_reader.get_person_info()
                    id_relative.set(info['cid'])
                except Exception as e:
                    print(f'เกิดข้อผิดพลาดในการอ่านบัตรประชาชน: {e}')
                    messagebox.showerror('ข้อผิดพลาด', 'ไม่สามารถอ่านบัตรประชาชนได้ กรุณากรอกข้อมูลด้วยตนเอง')
                    pass
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
                    # messagebox.showwarning('แจ้งเตือน',f'ไม่พบข้อมูลหมายเลข {popup_entry_id_relative.get().strip()} กรุณากรอกข้อมูลเพื่อลงทะเบียน')
                    try:
                        popup_combo_title_relative.set(info['title'])
                        popup_combo_title_relative.configure(state = 'normal')
                        f_name_var.set(info['firstname'])
                        popup_entry_fname_relative.configure(state = 'normal')
                        l_name_var.set(info['lastname'])
                        popup_entry_lname_relative.configure(state = 'normal')
                        address_var.set(info['address'])
                        popup_entry_address_relative.configure(state = 'normal')
                        tel_var.set('')
                        popup_entry_tel_relative.configure(state = 'normal')
                    except:
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
                        pass
 
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

        def show_relative(prisoner_id, f_name, l_name):
            print('show_relative fn')
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
                    confirm_delete = messagebox.askyesno('การลบข้อมูล',f'ต้องการลบข้อมูลของ {relative_name} หรือไม่')
                    if confirm_delete:
                        result_delete = self.db.delete_relation_from_prisoner_and_relative(prisoner_id,relative_id)
                        if result_delete:
                            messagebox.showinfo('ลบข้อมูล','ลบข้อมูลของเสร็จสิ้น')
                            result = self.db.get_join_prisoners_and_relatives_alldata(prisoner_id)
                            print(result)
                            for row in tree_relative.get_children():
                                tree_relative.delete(row)
                            for row in result:
                                tree_relative.insert('','end',values=row)


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
            popup_show_list.geometry('720x480+1+1')
            popup_show_list.grab_set()
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

            scrollbar = ttk.Scrollbar(tree_container_relative,orient='vertical',command=tree.yview)
            tree_relative.configure(yscrollcommand=scrollbar.set)
            tree_relative.grid(row=1,column=0,sticky='nsew')
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
            print('prisoner_id = ',prisoner_id)
            result = self.db.get_join_prisoners_and_relatives_alldata(prisoner_id)
            print('in show_relative ',result)
            for row in result:
                tree_relative.insert('','end',values=row)

            popup_window_delete_relative = None
            tree_relative.bind('<Configure>',lambda e:resize_tree_columns())
            tree_relative.bind("<Button-3>",show_menu_delete_relation)
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

            def update_level_and_dan():
                id = id_data.cget('text')
                sex = sex_data.get()
                f_name = fname_data.get().strip()
                l_name = lname_data.get().strip()
                lawsuit = lawsuit_data.get("1.0", ctk.END).strip()
                level = level_data.get()
                dan = dan_data.get()
                result =  self.db.update_level_and_dan(id,sex,f_name,l_name,lawsuit,level,dan,type_data.get(),status_data.get())
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

            search_frame = ctk.CTkFrame(popup_move_dan)
            search_frame.pack(fill='both',expand = True)

            search_frame.grid_columnconfigure((0,1),weight=1,uniform='move_adjust',minsize=100)
            search_frame.grid_rowconfigure((0,1,2,3,4,5,6,7,8,9,10),weight=1,uniform='move_adjust')

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
        
            id_data = ctk.CTkLabel(search_frame,text='',font=('TH SarabunPSK',18))
            sex_data = ctk.CTkOptionMenu(search_frame,values=['ชาย','หญิง'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
            fname_data = ctk.CTkEntry(search_frame,font=('TH SarabunPSK',18))
            lname_data = ctk.CTkEntry(search_frame,font=('TH SarabunPSK',18))
            lawsuit_data = ctk.CTkTextbox(search_frame,font=('TH SarabunPSK',18),height=60)
            level_data = ctk.CTkOptionMenu(search_frame,values=['ระหว่างพิจารณาคดี','เยี่ยม','ดีมาก','ดี','กลาง','ปรับปรุง','ปรับปรุงมาก'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
            dan_data = ctk.CTkOptionMenu(search_frame,values=['1','2','3','4','5','6','7','รจช'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
            type_data = ctk.CTkOptionMenu(search_frame,values=['ผู้ต้องขัง','ผู้ต้องกักขัง'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
            status_data = ctk.CTkOptionMenu(search_frame,values=['อยู่','ไม่อยู่'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))

            id_data.grid(row = 1,column = 1,sticky = 'w',padx = 5)
            sex_data.grid(row = 2,column = 1,sticky = 'w',padx = 5)
            fname_data.grid(row = 3,column = 1,sticky = 'w',padx = 5)
            lname_data.grid(row = 4,column = 1,sticky = 'w',padx = 5)
            lawsuit_data.grid(row = 5,column = 1 ,sticky = 'w',padx = 5)
            level_data.grid(row = 6,column = 1,sticky = 'w',padx = 5)
            dan_data.grid(row = 7,column = 1,sticky = 'w',padx = 5)
            type_data.grid(row = 8,column = 1,sticky = 'w',padx = 5)
            status_data.grid(row = 9,column = 1,sticky = 'w',padx = 5)

            button_submit = ctk.CTkButton(search_frame,
                                                        text='บันทึกข้อมูล',
                                                        width=100,
                                                        font=('TH SarabunPSK',18,'bold'),
                                                        command=lambda:update_level_and_dan()
                                                        )
            button_submit.grid(row = 10,column = 0,columnspan = 2,sticky = 'n',padx = 5)

            popup_move_dan.grid_columnconfigure((0,1),minsize=200)
            get_data_on_data_one()
            popup_move_dan.protocol("WM_DELETE_WINDOW", on_close)

#############################################################################

        # insert ข้อมูลให้อยู่ในตาราง treeview
        def show_prisoners(data):
            for row in tree.get_children():
                tree.delete(row)
            for row in data:
                tree.insert('','end',values=row)

        # ค้นหาข้อมูลจากตาราง แค่คนเดียว 
        def search_one_var_prisoners():
            nonlocal all_data
            keyword = search_all_var.get().lower()
            filtered = [
                row for row in all_data 
                if keyword in row[2].lower() or keyword in row[3].lower()
            ]
            print(filtered)
            show_prisoners(filtered)

        def resize_tree_columns():
            tree_container.update_idletasks()
            total_width = tree_container.winfo_width()
            for col, ratio in column_ratios.items():
                tree.column(col,width=int(total_width * ratio),anchor='w')

        def load_data_on_db():
            nonlocal all_data
            all_data = []
            all_data = self.db.get_data_all()
            show_prisoners(all_data)

        self.show_all_prisoner_frame.grid_rowconfigure(2,weight=1)
        self.show_all_prisoner_frame.grid_columnconfigure(0,weight=1)

        search_all_var = tk.StringVar()
        
        # หัวข้อ
        ctk.CTkLabel(self.show_all_prisoner_frame,text='ผู้ต้องขังทั้งหมด',font=('TH SarabunPSK',40,'bold')).grid(row = 0,column = 0,pady = 10,sticky = 'n')

        # ช่องค้นหา
        search_entry = ctk.CTkEntry(self.show_all_prisoner_frame,placeholder_text='พิมพ์ชื่อเพื่อค้นหา...',font=('TH SarabunPSK',18),width=200,textvariable=search_all_var)
        search_entry.grid(row = 1,column = 0, pady = 10,sticky = 'n')
        search_all_var.trace_add("write",lambda *args:search_one_var_prisoners())

        tree_container = ctk.CTkFrame(self.show_all_prisoner_frame)
        tree_container.grid(row = 2,column=0,padx=20, pady=10, sticky="nsew")

        tree_container.grid_rowconfigure(0,weight=1)
        tree_container.grid_columnconfigure(0,weight=1)

        # กำหนด style สำหรับ treeview 
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Treeview',font =('TH SarabunPSK',16),rowheight = 28)
        style.configure('Treeview.Heading',font = ('TH SarabunPSK',16,'bold'))

        tree = ttk.Treeview(tree_container,columns=('prisoner_id','sex','f_name','l_name','lawsuit','level','dan','type','status'),show='headings',height=10)
        tree.heading('prisoner_id',text='รหัสประจำตัว')
        tree.heading('sex',text='เพศ')
        tree.heading('f_name',text='ชื่อ')
        tree.heading('l_name',text='นามสกุล')
        tree.heading('lawsuit',text='คดี')
        tree.heading('level',text='ชั้น')
        tree.heading('dan',text='แดน')
        tree.heading('type',text='ประเภท')
        tree.heading('status',text='สถานะ')

        tree.column('prisoner_id')
        tree.column('sex')
        tree.column('f_name')
        tree.column('l_name')
        tree.column('lawsuit')
        tree.column('level')
        tree.column('dan')
        tree.column('type')
        tree.column('status')

        scrollbar = ttk.Scrollbar(tree_container,orient='vertical',command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.grid(row=0,column=0,sticky='nsew')
        scrollbar.grid(row=0,column=1,sticky='ns')

        column_ratios = {
            'prisoner_id' : 0.10,
            'sex' : 0.06,
            'f_name' : 0.13,
            'l_name' : 0.13,
            'lawsuit' : 0.18,
            'level' : 0.12,
            'dan' : 0.06,
            'type' : 0.11,
            'status' : 0.11
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

            # สร้าง popup window
            popup_window = ctk.CTkToplevel()
            popup_window.overrideredirect(True)  # ไม่มีกรอบ
            popup_window.geometry(f"+{event.x_root}+{event.y_root}")
            popup_window.configure(fg_color="#f0f0f0")

            # เพิ่มปุ่มใน popup
            def add_rel():
                popup_window.destroy()
                add_relative(prisoner_id, f_name, l_name)

            def show_rel():
                popup_window.destroy()
                print('show relative')
                show_relative(prisoner_id, f_name, l_name)

            def move_dan():
                popup_window.destroy()
                move_dan_and_adjust_level(prisoner_id)

            def delete_rel():
                popup_window.destroy()
                confirm_delete = messagebox.askyesno('ยืนยันลบข้อมูล',f'ลบข้อมูลของ {f_name} {l_name}')
                # print(type(prisoner_id))
                if confirm_delete:
                    result_delete = self.db.delete_prisoner(prisoner_id)
                    if result_delete:
                        messagebox.showinfo('ลบข้อมูล','ลบข้อมูลเสร็จสิ้น')
                        load_data_on_db()
                    else:
                        messagebox.showerror('ลบข้อมูล','ลบข้อมูลไม่สำเร็จ')

            # สร้างปุ่มใน popup
            ctk.CTkButton(popup_window, text="➕ เพิ่มญาติ",font =('TH SarabunPSK',18,'bold'), command=add_rel, width=160).pack(padx=10, pady=(10, 5))
            ctk.CTkButton(popup_window, text="👥 ดูรายชื่อญาติ",font =('TH SarabunPSK',18,'bold'), command=show_rel, width=160).pack(padx=10, pady=5)
            ctk.CTkButton(popup_window, text="➡️ แก้ไขข้อมูลผู้ต้องขัง",font =('TH SarabunPSK',18,'bold'), command=move_dan, width=160).pack(padx=10, pady=5)
            ctk.CTkButton(popup_window, text="🗑️ ลบชื่อญาติ",font =('TH SarabunPSK',18,'bold'), command=delete_rel, width=160, fg_color="red").pack(padx=10, pady=(5, 10))

            # เมื่อคลิกข้างนอก popup ให้ปิด
            popup_window.bind("<FocusOut>", lambda e: popup_window.destroy())
            popup_window.focus_set()

        # ผูกกับคลิกขวา
        tree.bind("<Button-3>", show_ctk_popup)
        tree.bind('<Configure>',lambda e:resize_tree_columns())
        popup_window = None
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
            popup_window_all_relative.configure(fg_color = '#f0f0f0')

            def show_rel():
                popup_window_all_relative.destroy()
                print(relative_id,relative_name)
                show_relative(relative_id,relative_name)

            def edit_rel():
                popup_window_all_relative.destroy()
                edit_relative(relative_id)

            ctk.CTkButton(popup_window_all_relative,text='ดูรายชื่อผุ้ต้องขัง',font =('TH SarabunPSK',18,'bold'),command=show_rel,width=160).pack(padx = 10,pady = (10,5))
            ctk.CTkButton(popup_window_all_relative,text='แก้ไขข้อมูล',font =('TH SarabunPSK',18,'bold'),command=edit_rel,width=160).pack(padx = 10,pady = (10,5))

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

            relative_frame = ctk.CTkFrame(popup_edit_relative)
            relative_frame.pack(fill='both',expand = True)

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
            for row in data:
                tree.insert('','end',values=row)

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
            all_data = self.db.get_all_relatives()
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

            label_national_id = ctk.CTkLabel(show_regis_data_search,text='รหัสประจำตัว : ',font=('TH SarabunPSK',18,'bold'))
            label_national_id.grid(row = 0,column = 0,padx = 5,sticky = 'e')

            entry_national_id = ctk.CTkEntry(show_regis_data_search,textvariable=show_regis_id_var,state = 'disabled',font=('TH SarabunPSK',18))
            entry_national_id.grid(row = 0,column = 1,padx = 5,sticky = 'w')

            label_title = ctk.CTkLabel(show_regis_data_search,text='คำนำหน้า : ',font=('TH SarabunPSK',18,'bold'))
            label_title.grid(row = 1,column = 0,sticky = 'e',padx = 5)

            combo_title = ctk.CTkOptionMenu(show_regis_data_search,values=['นาย','นาง','นางสาว','เด็กหญิง','เด็กชาย'],variable=show_regis_title,font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
            combo_title.grid(row = 1,column = 1,sticky = 'w',padx = 5)

            label_f_name = ctk.CTkLabel(show_regis_data_search,text='ชื่อ : ',font=('TH SarabunPSK',18,'bold'))
            label_f_name.grid(row = 2,column = 0,padx= 5,sticky = 'e')

            entry_f_name = ctk.CTkEntry(show_regis_data_search,font=('TH SarabunPSK',18),textvariable=show_regis_entry_fname_var)
            entry_f_name.grid(row = 2,column = 1,padx= 5,sticky = 'w')

            label_l_name = ctk.CTkLabel(show_regis_data_search,text='นามสกุล : ',font=('TH SarabunPSK',18,'bold'))
            label_l_name.grid(row = 3,column = 0,padx= 5,sticky = 'e')

            entry_l_name = ctk.CTkEntry(show_regis_data_search,font=('TH SarabunPSK',18),textvariable=show_regis_entry_lname_var)
            entry_l_name.grid(row = 3,column = 1,padx= 5,sticky = 'w')

            label_address = ctk.CTkLabel(show_regis_data_search,text='ที่อยู่ : ',font=('TH SarabunPSK',18,'bold'))
            label_address.grid(row = 4,column = 0,padx= 5,sticky = 'e')

            entry_address = ctk.CTkEntry(show_regis_data_search,font=('TH SarabunPSK',18),textvariable=show_regis_entry_address_var)
            entry_address.grid(row = 4,column = 1,padx= 5,sticky = 'w')

            label_tel = ctk.CTkLabel(show_regis_data_search,text='เบอร์โทร : ',font=('TH SarabunPSK',18,'bold'))
            label_tel.grid(row = 5,column = 0,padx= 5,sticky = 'e')

            entry_tel = ctk.CTkEntry(show_regis_data_search,font=('TH SarabunPSK',18),textvariable=show_regis_entry_tel_var)
            entry_tel.grid(row = 5,column = 1,padx= 5,sticky = 'w')

            label_fingerprint = ctk.CTkLabel(show_regis_data_search,text='ลายนิ้วมือ : ',font=('TH SarabunPSK',18,'bold'))
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
                    messagebox.showerror('Error การอ่านบัตรประชาชน','กรุณาตรวจสอบการเชื่อมต่อเครื่องอ่านบัตรประชาชน')
                    return 
                return info['cid']
            if read_card():
                regis_fp_entry.delete(0,tk.END)
                regis_fp_entry.insert(0,read_card())
            if not regis_fp_entry.get():
                messagebox.showwarning('แจ้งเตือน','กรุณากรอกข้อมูล')
            else:
                result = self.db.get_data_for_ralative_id(regis_fp_entry.get().strip())
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
                    get_data_relative()
                    # insert_fingerprint_to_db()

                threading.Thread(target=run, daemon=True).start()
            
        def on_close():
            print('ปิดหน้าต่าง popup_register_fingerprint')
            popup_register_fingerprint.destroy()

        popup_register_fingerprint = ctk.CTkToplevel(self)
        popup_register_fingerprint.title('ลงทะเบียนลายนิ้วมือ')
        popup_register_fingerprint.geometry('480x720+1+1')
        popup_register_fingerprint.grab_set()

        popup_register_fingerprint.grid_rowconfigure(2,weight=1,uniform='regis_fg')
        popup_register_fingerprint.grid_columnconfigure((0,1),weight=1,uniform='regis_fg')


        show_regis_id_var = ctk.StringVar()
        show_regis_title = ctk.StringVar()
        show_regis_entry_fname_var = ctk.StringVar()
        show_regis_entry_lname_var = ctk.StringVar()
        show_regis_entry_address_var = ctk.StringVar()
        show_regis_entry_tel_var = ctk.StringVar()

        ctk.CTkLabel(popup_register_fingerprint,text='ลงทะเบียนลายนิ้วมือ',font=('TH SarabunPSK',28,'bold')).grid(row = 0,column = 0,columnspan = 2,sticky = 'nsew',pady = 30)

        regis_fp_entry = ctk.CTkEntry(popup_register_fingerprint,width=150,font=('TH SarabunPSK',18),validate='key',validatecommand = (self.vcmd,'%P'))
        regis_fp_entry.grid(row = 1,column = 0,sticky = 'e',padx = 5,pady = 10)

        regis_fp_search_bt = ctk.CTkButton(popup_register_fingerprint,
                                                text='ค้นหาข้อมูล',
                                                width=150,
                                                font=('TH SarabunPSK',18,'bold'),
                                                command=lambda:get_data_relative())
        regis_fp_search_bt.grid(row=1,column = 1,sticky = 'w',padx = 5,pady = 10)
        show_regis_data_search = ctk.CTkFrame(popup_register_fingerprint)
        label_fingerprint_state = ctk.CTkLabel(show_regis_data_search,font=('TH SarabunPSK',18,'bold'),text='')

        popup_register_fingerprint.protocol("WM_DELETE_WINDOW", on_close)
##############################################################################################################################################################################
    # รายการจองเยี่ยม
##############################################################################################################################################################################
    def reserve_to_visit(self):
       
        def config_label():
            relative_label.grid_forget()
            tree_container.grid_forget()
            progressbar.grid(row = 2,column = 0 ,columnspan = 2,pady = 20)
            progressbar.stop()
            label_content.grid(row = 3,column = 0,columnspan = 2 ,sticky = 'nsew',pady = 20)
            date_label.grid(row=0,column=0,columnspan=2,sticky='n', pady=10)
            label_content.configure(text = 'กรุณาวางนิ้วมือบนเครื่องสแกนเพื่อเริ่มทำรายการ',text_color = 'black')
            update_time_label()
            get_relative()

        def update_time_label():
            text = f"วัน {day} ที่ {current_time.tm_mday} {month} {(current_time.tm_year)+543} เวลา {t.strftime('%H:%M:%S')}"
            date_label.configure(text=text)
            if popup_reserve_to_visit.winfo_exists():
                popup_reserve_to_visit.after(1000,update_time_label)

        def get_capture_fingerprint():
            def run():
                nonlocal capture_current,flag_status,nationnal_id
                nationnal_id = None
                try:
                    capture = self.zkfp2.AcquireFingerprint()
                except Exception as e:
                    messagebox.showerror('Error เครื่องสแกน','กรุณาตรวจสอบเครื่องสแกน')
                if capture:
                    label_content.configure(text = 'ตรวจพบลายนิ้วมือ\nกรุณารอสักครู่ ระบบกำลังตรวจสอบ')
                    print('สแกนสำเร็จ',type(capture_current))
                    tmp, img = capture
                    capture_current = tmp
                    result = self.db.get_all_fingerprint()
                    
                    for row in result:
                        fingerprint_in_db = row[4]
                        if fingerprint_in_db:
                            res = self.zkfp2.DBMatch(tmp,fingerprint_in_db)
                            if res > 80 :
                                nationnal_id = row[0]
                                relative_data = f'{row[1]}{row[2]} {row[3]}'
                                break

                    if nationnal_id:
                        prisoners_data = self.db.get_join_relatives_and_prisoners(nationnal_id)
                    else:
                        label_content.configure(text = '\n\n\nไม่พบลายนิ้วมือ\nกรุณาเตรียมบัตรประชาชนเพื่อติดต่อเจ้าหน้าที่',text_color = 'red')
                        progressbar.grid(row = 2,column = 0 ,columnspan = 2,pady = 20)
                        self.after(2000,config_label)
                        return
                    
                    progressbar.stop()
                    flag_status = False
                    progressbar.grid_forget()
                    label_content.grid_forget()

                    allowed_dan_by_dan = {
                        "จันทร์" : ['6','รจช'],
                        "อังคาร" : ['5','รจช'],
                        "พุธ" : ['1','2','3','4','7','รจช'],
                        "พฤหัสบดี" : ['5','6','รจช'],
                        "ศุกร์" : ['1','2','3','4','7','รจช']
                        
                    }

                    allower_dan = allowed_dan_by_dan.get(day,[])
                    print(f'วันนี้ = {day}')
                    for row in prisoners_data:
                        print(f'ข้อมูลใน prisoner_data : {row}')
                    for row in tree.get_children():
                        tree.delete(row)

                    for index,row in enumerate(prisoners_data):
                        if row[4] not in allower_dan:
                            continue
                        tree.insert('','end',values=row)

                    if len(tree.get_children()) == 0:
                        alert = ALERT(popup_reserve_to_visit,['ไม่พบข้อมูลผู้ต้องขังที่เยี่ยมได้\nกรุณาตรวจสอบวันและเวลาเยี่ยม'],button=False)
                        alert.after(3000,lambda: (alert.destroy(),config_label()))
                    else:

                        relative_label.configure(text =f'ยินดีต้อนรับ {relative_data} กรุณากดเลือกเพื่อจองเยี่ยม' )
                        relative_label.grid(row=1,column=0,columnspan=2,sticky='nsew' )
                        tree.grid(row=1,column=0,columnspan=2,sticky='nsew')
                        tree_container.grid(row = 2,column=0,columnspan = 2,padx=20, pady=10, sticky="nsew")
                        scrollbar.grid(row=1,column=1,sticky='ns')
                else:
                    if popup_reserve_to_visit.winfo_exists():
                        self.after(500,get_capture_fingerprint)
            threading.Thread(target=run,daemon=True).start()

        def get_relative():
            nonlocal flag_status
            if not flag_status:
                progressbar.grid(row = 2,column = 0 ,columnspan = 2,pady = 20)
                progressbar.start()
                flag_status = True
            # try:
            #     self.zkfp2.Init()
            #     self.zkfp2.OpenDevice(0)
            # except Exception as e:
            #     print(f'เกิดข้อผิดพลาด get_relative() : {e}')
            #     messagebox.showerror('การเชื่อมต่อเครื่อง','กรุณาตรวจสอบการเชื่อต่อเครื่องสแกนลายนิ้วมือ')
            #     on_close()
            #     return
            get_capture_fingerprint()

        def item_select(_):
            try:
                for i in tree.selection():
                    prisoner_data = tree.item(i)['values']
                    break
                if self.open_nextscreen_window is None or not self.open_nextscreen_window.winfo_exists():
                    self.open_nextscreen_window = open_next_screen(prisoner_data)
                else:
                    self.open_nextscreen_window.lift()
            except Exception as e:
                print(f'เกิดข้อผิดพลาด item_select(_) : {e}')

        def on_close(e = None):
            try:
                self.zkfp2.CloseDevice()
                print('Close Device')
            except Exception as e:
                print(f'ปิดอุปกรณ์ลายนิ้วมือไม่สำเร็จ : {e}')
            try:
                popup_reserve_to_visit.destroy()
            except Exception:
                pass

        def can_reserve_for_next_day():
            now = datetime.now()
            if now.hour > 14 or (now.hour == 14 and now.minute >= 0):
                return True
            return False

        def get_next_reserve_date():
            # คืนค่าวันถัดไปในรูปแบบ YYYY-MM-DD
            return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        def open_next_screen(data):
            
            # ตรวจสอบว่าวันนี้ได้เยี่ยมแล้วหรือยัง psn_id คือ prisoner_id
            psn_id = data[0]
            psn_level = data[3]
            today = datetime.today().date().isoformat()
            today_month = datetime.today().strftime('%Y-%m')
            check_visit = self.db.get_count_visit(psn_id,today,today_month) # index 0 count_day index 1 coutn_month
            print(type(check_visit[1]))

            reserve_date = datetime.now().strftime("%Y-%m-%d")

            if can_reserve_for_next_day():
                reserve_date = get_next_reserve_date()

            if check_visit[0] > 0 :
                alert = ALERT(popup_reserve_to_visit,['กรุณาตรวจสอบข้อมูล\nผู้ต้องขังเยี่ยมได้ไม่เกิน 1 ครั้ง ต่อวัน'],button=False)
                alert.after(3000,lambda: (alert.destroy(),config_label()))
                return
            if psn_level == 'เยี่ยม' and check_visit[1] >= 8 :
                alert = ALERT(popup_reserve_to_visit,[f'กรุณาตรวจสอบข้อมูล\nชั้น {psn_level}\nเยี่ยมได้ไม่เกิน 8 ครั้ง ต่อเดือน'],button=False)
                alert.after(3000,lambda: (alert.destroy(),config_label()))
                return
            if psn_level == 'ดีมาก' and check_visit[1] >= 6 :
                alert = ALERT(popup_reserve_to_visit,[f'กรุณาตรวจสอบข้อมูล\nชั้น {psn_level}\nเยี่ยมได้ไม่เกิน 6 ครั้ง ต่อเดือน'],button=False)
                alert.after(3000,lambda: (alert.destroy(),config_label()))
                return
            if psn_level == 'ดี' and check_visit[1] >= 4 :
                alert = ALERT(popup_reserve_to_visit,[f'กรุณาตรวจสอบข้อมูล\nชั้น {psn_level}\nเยี่ยมได้ไม่เกิน 4 ครั้ง ต่อเดือน'],button=False)
                alert.after(3000,lambda: (alert.destroy(),config_label()))
                return
            if psn_level == 'กลาง' and check_visit[1] >= 3 :
                alert = ALERT(popup_reserve_to_visit,[f'กรุณาตรวจสอบข้อมูล\nชั้น {psn_level}\nเยี่ยมได้ไม่เกิน 3 ครั้ง ต่อเดือน'],button=False)
                alert.after(3000,lambda: (alert.destroy(),config_label()))
                return
            if psn_level == 'ระหว่างพิจารณาคดี' and check_visit[1] >= 3 :
                alert = ALERT(popup_reserve_to_visit,[f'กรุณาตรวจสอบข้อมูล\nชั้น {psn_level}\nเยี่ยมได้ไม่เกิน 3 ครั้ง ต่อเดือน'],button=False)
                alert.after(3000,lambda: (alert.destroy(),config_label()))
                return
            if psn_level == 'ปรับปรุง' and check_visit[1] >= 2 :
                alert = ALERT(popup_reserve_to_visit,[f'กรุณาตรวจสอบข้อมูล\nชั้น {psn_level}\nเยี่ยมได้ไม่เกิน 2 ครั้ง ต่อเดือน'],button=False)
                alert.after(3000,lambda: (alert.destroy(),config_label()))
                return
            if psn_level == 'ปรับปรุงมาก' and check_visit[1] >= 1 :
                alert = ALERT(popup_reserve_to_visit,[f'กรุณาตรวจสอบข้อมูล\nชั้น {psn_level}\nเยี่ยมได้ไม่เกิน 1 ครั้ง ต่อเดือน'],button=False)
                alert.after(3000,lambda: (alert.destroy(),config_label()))
                return


            relative_dict = {}
            data_relatives = self.db.get_relatives_id_fname_lname()
            for rel_id,f_name,l_name in data_relatives:
                full_name = f'{f_name} {l_name}'
                relative_dict[rel_id] = full_name

            next_screen = ctk.CTkToplevel(popup_reserve_to_visit)
            next_screen.geometry('400x750')
            next_screen.title('เลือกรอบเยี่ยม')
            next_screen.grab_set()
            next_screen.attributes('-topmost',True)
            next_screen.minsize(400,750)
            next_screen.maxsize(400,750)
            prisoner_id = data[0]
            # frame เลือกรอบ
            frame_select_round = ctk.CTkFrame(next_screen)
            # frame เลือกผู้ติดตาม
            frame_follower_visit = ctk.CTkFrame(next_screen)
            # frame ยืนยันการจอง
            frame_confirm_visit = ctk.CTkFrame(next_screen)

            round_visit_var = ctk.StringVar()
            follower_vars = []

            def next_screen_on_close():
                
                self.open_nextscreen_window = None
                tree_container.grid_forget()
                relative_label.grid_forget()
                next_screen.destroy()
                config_label()

            def select_round():
                for widget in frame_select_round.winfo_children():
                    widget.destroy()

                frame_follower_visit.pack_forget()
                frame_select_round.pack(fill='both', expand=True)

                label = ctk.CTkLabel(frame_select_round, text='เลือกรอบเยี่ยม', font=('TH SarabunPSK', 40, 'bold'))
                label.pack(pady=5)
                content = ctk.CTkLabel(frame_select_round, text=f'{data[1]} {data[2]}', font=('TH SarabunPSK', 30))
                content.pack(pady=5)

                now = datetime.now().time()
                print(day)
                print(data[4])
                late_time = datetime.strptime('14:00:00', "%H:%M:%S").time()


                if data[4] == 'รจช':
                    # 🔹 รอบเช้า (เวลาแสดง, เวลาเริ่มจริง, เวลาปิด)
                    rounds = [
                        ('เวลา 12.00 - 13.00', '12:00:00', '12:50:00')
                    ]
                    for text, start, close in rounds:
                        close_time = datetime.strptime(close, "%H:%M:%S").time()
                        if now < close_time:
                            ctk.CTkRadioButton(
                                frame_select_round,
                                text=text,
                                variable=round_visit_var,
                                value=start,
                                font=('TH SarabunPSK', 32, 'bold')
                            ).pack(pady=5)

                elif (day == 'จันทร์' and data[4] == 6) or (day in ['จันทร์','อังคาร','พุธ','พฤหัสบดี'] and data[4] == 5):
                    # 🔹 รอบเช้า (เวลาแสดง, เวลาเริ่มจริง, เวลาปิด)
                    morning_rounds = [
                        ('รอบที่ 1 เวลา 09.30 - 09.45', '09:30:00', '09:15:00'),
                        ('รอบที่ 2 เวลา 10.00 - 10.15', '10:00:00', '09:45:00'),
                        ('รอบที่ 3 เวลา 10.30 - 10.45', '10:30:00', '10:15:00'),
                        ('รอบที่ 4 เวลา 11.00 - 11.15', '11:00:00', '10:15:00'),
                    ]

                    ctk.CTkLabel(frame_select_round, text='รอบเช้า', font=('TH SarabunPSK', 32, 'bold')).pack(pady=10)
                    for text, start, close in morning_rounds:
                        close_time = datetime.strptime(close, "%H:%M:%S").time()
                        if now < close_time:
                            ctk.CTkRadioButton(
                                frame_select_round,
                                text=text,
                                variable=round_visit_var,
                                value=start,
                                font=('TH SarabunPSK', 32, 'bold')
                            ).pack(pady=5)
                        elif now > late_time:
                            ctk.CTkRadioButton(
                                frame_select_round,
                                text=text,
                                variable=round_visit_var,
                                value=start,
                                font=('TH SarabunPSK', 32, 'bold')
                            ).pack(pady=5)

                    # 🔹 รอบบ่าย
                    afternoon_rounds = [
                        ('รอบที่ 5 เวลา 13.15 - 13.30', '13:15:00', '13:00:00'),
                        ('รอบที่ 6 เวลา 13.45 - 14.00', '13:45:00', '13:15:00'),
                        ('รอบที่ 7 เวลา 14.15 - 14.30', '14:15:00', '13:15:00'),
                    ]

                    ctk.CTkLabel(frame_select_round, text='รอบบ่าย', font=('TH SarabunPSK', 32, 'bold')).pack(pady=10)
                    for text, start, close in afternoon_rounds:
                        close_time = datetime.strptime(close, "%H:%M:%S").time()
                        if now < close_time:
                            ctk.CTkRadioButton(
                                frame_select_round,
                                text=text,
                                variable=round_visit_var,
                                value=start,
                                font=('TH SarabunPSK', 32, 'bold')
                            ).pack(pady=5)
                        
                        elif now > late_time:
                            ctk.CTkRadioButton(
                                frame_select_round,
                                text=text,
                                variable=round_visit_var,
                                value=start,
                                font=('TH SarabunPSK', 32, 'bold')
                            ).pack(pady=5)

                elif (day in ['อังคาร','พุธ'] and data[4] == 1) or (day in ['พฤหัสบดี','ศุกร์'] and data[4] == 1):
                    # 🔹 รอบเช้า (เวลาแสดง, เวลาเริ่มจริง, เวลาปิด)
                    morning_rounds = [
                        ('รอบที่ 1 เวลา 09.30 - 09.45', '09:30:00', '09:15:00'),
                        ('รอบที่ 2 เวลา 10.00 - 10.15', '10:00:00', '09:45:00'),
                        ('รอบที่ 3 เวลา 10.30 - 10.45', '10:30:00', '10:15:00'),
                        ('รอบที่ 4 เวลา 11.00 - 11.15', '11:00:00', '10:15:00'),
                    ]

                    ctk.CTkLabel(frame_select_round, text='รอบเช้า', font=('TH SarabunPSK', 32, 'bold')).pack(pady=10)
                    for text, start, close in morning_rounds:
                        close_time = datetime.strptime(close, "%H:%M:%S").time()
                        if now < close_time:
                            ctk.CTkRadioButton(
                                frame_select_round,
                                text=text,
                                variable=round_visit_var,
                                value=start,
                                font=('TH SarabunPSK', 32, 'bold')
                            ).pack(pady=5)
                        elif now > late_time:
                            ctk.CTkRadioButton(
                                frame_select_round,
                                text=text,
                                variable=round_visit_var,
                                value=start,
                                font=('TH SarabunPSK', 32, 'bold')
                            ).pack(pady=5)

                elif (day in ['อังคาร','พุธ'] and data[4] in [2,3,4,7]) or (day in ['พฤหัสบดี','ศุกร์'] and data[4] in [2,3,4,7]):
                    # 🔹 รอบบ่าย
                    afternoon_rounds = [
                        ('รอบที่ 5 เวลา 13.15 - 13.30', '13:15:00', '13:00:00'),
                        ('รอบที่ 6 เวลา 13.45 - 14.00', '13:45:00', '13:15:00'),
                        ('รอบที่ 7 เวลา 14.15 - 14.30', '14:15:00', '13:15:00'),
                    ]

                    ctk.CTkLabel(frame_select_round, text='รอบบ่าย', font=('TH SarabunPSK', 32, 'bold')).pack(pady=10)
                    for text, start, close in afternoon_rounds:
                        close_time = datetime.strptime(close, "%H:%M:%S").time()
                        if now < close_time:
                            ctk.CTkRadioButton(
                                frame_select_round,
                                text=text,
                                variable=round_visit_var,
                                value=start,
                                font=('TH SarabunPSK', 32, 'bold')
                            ).pack(pady=5)
                        elif now > late_time:
                            ctk.CTkRadioButton(
                                frame_select_round,
                                text=text,
                                variable=round_visit_var,
                                value=start,
                                font=('TH SarabunPSK', 32, 'bold')
                            ).pack(pady=5)
                            
                # 🔸 ปุ่ม
                submit = ctk.CTkButton(
                    frame_select_round,
                    text='เลือกผู้ติดตาม',
                    command=lambda: select_follower() if round_visit_var.get() else ALERT(frame_select_round, msg=['\nกรุณาเลือกรอบเยี่ยม']),
                    font=('TH SarabunPSK', 24, 'bold'),
                    height=100
                )

                cancel = ctk.CTkButton(
                    frame_select_round,
                    text='ยกเลิก',
                    command=next_screen_on_close,
                    font=('TH SarabunPSK', 24, 'bold'),
                    height=40,
                    fg_color='red'
                )

                cancel.pack(side='bottom', pady=10)
                submit.pack(side='bottom', pady=10)

            def select_follower():
                for widget in frame_follower_visit.winfo_children():
                    widget.destroy()
                frame_select_round.pack_forget()
                frame_confirm_visit.pack_forget()

                # date time จากการเลือกรอบเยี่ยม
                round_time = round_visit_var.get()
                round_time_strtime = (datetime.strptime(round_time,"%H:%M:%S")).strftime("%H:%M:%S")
                count_visit = self.db.get_count_visit_on_round(round_time,reserve_date)
                
                print(f'count_visit = {count_visit}')

                if count_visit > 14:
                    count_alert = ALERT(next_screen,['รอบเต็ม\nกรุณาเลือกรอบใหม่'],text_color='red',button=True)
                    select_round()
                    return
                                          
                frame_follower_visit.pack(fill = 'both',expand = True)
                text_from_round = f'จองเยี่ยม\n{data[1]} {data[2]}\nเยี่ยมเวลา {round_visit_var.get()} น.'
                ctk.CTkLabel(frame_follower_visit,text=text_from_round,font=('TH SarabunPSK',28)).pack(pady = 10)


                followers = self.db.get_join_prisoners_and_relatives_not_follower(prisoner_id,nationnal_id)
                ctk.CTkLabel(frame_follower_visit,text='กรุณาเลือกผู้ติดตาม',font=('TH SarabunPSK',32,'bold')).pack(pady = 10)
                ctk.CTkLabel(frame_follower_visit,text='(เลือกผู้ติดตามได้สูงสุด 4 คน)',text_color='red',font=('TH SarabunPSK',24,'bold')).pack(pady = 10)
                if followers:
                    for follower in followers:
                        rid,title,fname,lname = follower
                        var = ctk.BooleanVar()
                        chk = ctk.CTkCheckBox(frame_follower_visit,
                                              text=f'{title}{fname} {lname}',
                                              variable=var,
                                              font=('TH SarabunPSK',28,'bold'))
                        chk.pack(pady = 5,padx = 50,anchor = 'nw')
                        follower_vars.append((rid,var))
                else:
                    ctk.CTkLabel(frame_follower_visit,text='ไม่มีผู้ติดตาม',font=('TH SarabunPSK',28,'bold')).pack(pady = 10)

                submit = ctk.CTkButton(frame_follower_visit,
                                    text='ถัดไป',
                                    command=lambda:confirm_visit(round_time_strtime,reserve_date),
                                    font=('TH SarabunPSK',24,'bold'),
                                    height=100
                                    )
                
                cancel = ctk.CTkButton(frame_follower_visit,
                                    text='ย้อนกลับ',
                                    command=lambda:select_round(),
                                    font=('TH SarabunPSK',24,'bold'),
                                    height=40,
                                    fg_color='orange'
                                    )
                cancel.pack(side = 'bottom',pady = 10)
                submit.pack(side = 'bottom',pady = 10)

            def confirm_visit(round_time_strtime,reserve_date):
                for widget in frame_confirm_visit.winfo_children():
                    widget.destroy()

                frame_follower_visit.pack_forget()
                frame_confirm_visit.pack(fill = 'both',expand = True)
                ctk.CTkLabel(frame_confirm_visit,text='กรุณาตรวจสอบข้อมูลให้ถูกต้อง',font=('TH SarabunPSK',24,'bold')).pack(pady = 20)
                select_fl_id = [rid for rid,var in follower_vars if var.get()]
                prepare_data = [reserve_date,round_time_strtime,prisoner_id,nationnal_id]

                ctk.CTkLabel(frame_confirm_visit,text=f'จองเยี่ยม\n{data[1]} {data[2]}\nเวลา {round_visit_var.get()} น.\nโดย {relative_dict.get(nationnal_id)}\nผู้ติดตาม',font=('TH SarabunPSK',28)).pack(pady = 5)
                for index,row in enumerate(select_fl_id):
                    prepare_data.append(row)
                    ctk.CTkLabel(frame_confirm_visit,text=f'คนที่ {index +1} {relative_dict.get(row)}',font=('TH SarabunPSK',28)).pack(pady = 5)

                select_fl_id.clear()

                if len(prepare_data) > 8:
                    print(f'ใน if = {prepare_data}')
                    prepare_data.clear()
                    follower_vars.clear()
                    select_follower()
                    alert = ALERT(frame_follower_visit,msg=['เลือกผู้ติดตามได้ไม่เกิน 4 คน','กรุณาเลือกใหม่'])
                
                submit = ctk.CTkButton(frame_confirm_visit,
                                    text='ยืนยันการจองเยี่ยม',
                                    command=lambda:insert_reserve_visit_to_db(prepare_data),
                                    font=('TH SarabunPSK',24,'bold'),
                                    height=100
                                    )
            
                back = ctk.CTkButton(frame_confirm_visit,
                                    text='ย้อนกลับ',
                                    command=lambda:go_back() ,
                                    font=('TH SarabunPSK',24,'bold'),
                                    height=40,
                                    fg_color='orange'
                                    )
                cancel = ctk.CTkButton(frame_confirm_visit,
                                    text='ยกเลิกการจอง',
                                    command=lambda:next_screen_on_close(),
                                    font=('TH SarabunPSK',24,'bold'),
                                    height=40,
                                    fg_color='red'
                                    )
                cancel.pack(side = 'bottom',pady = 20)
                back.pack(side = 'bottom',pady = 20)
                submit.pack(side = 'bottom',pady = 20)

                def go_back():
                    prepare_data.clear()
                    follower_vars.clear()
                    select_follower()
                    
            def insert_reserve_visit_to_db(prepare_data):
                print(prepare_data)
                if len(prepare_data) == 8:
                    query = "INSERT INTO visits (date_visit,time_visit,prisoner_id,relative_id_1,relative_id_2,relative_id_3,relative_id_4,relative_id_5) VALUES (?,?,?,?,?,?,?,?)"
                    result = self.db.add_visits(query,prepare_data)
                    if result:
                        insert_succress()
                        return
                elif len(prepare_data) == 7:
                    query = "INSERT INTO visits (date_visit,time_visit,prisoner_id,relative_id_1,relative_id_2,relative_id_3,relative_id_4) VALUES (?,?,?,?,?,?,?)"
                    result = self.db.add_visits(query,prepare_data)
                    if result:
                        insert_succress()
                        return
                elif len(prepare_data) == 6:
                    query = "INSERT INTO visits (date_visit,time_visit,prisoner_id,relative_id_1,relative_id_2,relative_id_3) VALUES (?,?,?,?,?,?)"
                    result = self.db.add_visits(query,prepare_data)
                    if result:
                        insert_succress()
                        return
                elif len(prepare_data) == 5:
                    query = "INSERT INTO visits (date_visit,time_visit,prisoner_id,relative_id_1,relative_id_2) VALUES (?,?,?,?,?)"
                    result = self.db.add_visits(query,prepare_data)
                    if result:
                        insert_succress()
                        return
                elif len(prepare_data) == 4:
                    query = "INSERT INTO visits (date_visit,time_visit,prisoner_id,relative_id_1) VALUES (?,?,?,?)"
                    result = self.db.add_visits(query,prepare_data)
                    if result:
                        insert_succress()
                        return
                
            def insert_succress():
                alert = ALERT(next_screen,['จองเยี่ยมสำเร็จ'],button=True)
                result =alert.show()
                if result:
                    next_screen_on_close()
            
            select_round()
            next_screen.protocol("WM_DELETE_WINDOW", next_screen_on_close)
            return next_screen

        try:
            self.zkfp2.Init()
            self.zkfp2.OpenDevice(0)
        except Exception as e:
            messagebox.showerror('การเชื่อมต่อเครื่อง','กรุณาตรวจสอบการเชื่อมต่อเครื่องสแกนลายนิ้วมือ')
            on_close()
            return

        popup_reserve_to_visit = ctk.CTkToplevel(self) 
        popup_reserve_to_visit.title('จองเยี่ยม')
        popup_reserve_to_visit.geometry('1920x1080+1+1')
        popup_reserve_to_visit.grab_set()
        popup_reserve_to_visit.focus()
        popup_reserve_to_visit.attributes('-fullscreen',True)

        popup_reserve_to_visit.grid_columnconfigure((0,1),weight=1,uniform='popup_reserve')
        popup_reserve_to_visit.grid_rowconfigure(1,weight=0,uniform='popup_reserve')
        progressbar = ctk.CTkProgressBar(popup_reserve_to_visit,mode='indeterminate')
        label_content = ctk.CTkLabel(popup_reserve_to_visit,text='',font=('TH SarabunPSK', 52, 'bold'))
        date_label = ctk.CTkLabel(popup_reserve_to_visit,font=('TH SarabunPSK', 52, 'bold'))
        relative_label = ctk.CTkLabel(popup_reserve_to_visit,font=('TH SarabunPSK', 46, 'bold'))
        flag_status = False
        nationnal_id = None
        days = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์","อาทิตย์"]
        months = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน",
                    "พฤษภาคม","มิถุนายน","กรกฎาคม", "สิงหาคม",
                    "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]

        current_time = t.localtime()
        day = days[current_time.tm_wday]
        month = months[current_time.tm_mon - 1]


        capture_current = None

        tree_container = ctk.CTkFrame(popup_reserve_to_visit)
        tree_container.grid_rowconfigure(1,weight=1)
        tree_container.grid_columnconfigure(0,weight=1)
        config_label()
        # update_time_label()
        # get_relative()

        # กำหนด style สำหรับ treeview 
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Treeview',font =('TH SarabunPSK',18),rowheight = 35)
        style.configure('Treeview.Heading',font = ('TH SarabunPSK',18,'bold'))

        tree = ttk.Treeview(tree_container,columns=('prisoner_id','f_name','l_name','level','dan','relation'),show='headings',height=10)
        tree.heading('prisoner_id',text='รหัสประจำตัว')
        tree.heading('f_name',text='ชื่อ')
        tree.heading('l_name',text='นามสกุล')
        tree.heading('level',text='ชั้น')
        tree.heading('dan',text='แดน')
        tree.heading('relation',text='ความสัมพันธ์')

        tree.column('prisoner_id')
        tree.column('f_name')
        tree.column('l_name')
        tree.column('level')
        tree.column('dan')
        tree.column('relation')

        scrollbar = ttk.Scrollbar(tree_container,orient='vertical',command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.bind('<<TreeviewSelect>>',item_select)

        popup_reserve_to_visit.protocol("WM_DELETE_WINDOW", on_close)
        popup_reserve_to_visit.bind_all('<Alt-q>', on_close)

##############################################################################################################################################################################
    # รายการจองเยี่ยมด้วยเลขบัตรประชาชน
##############################################################################################################################################################################
    def reserve_visit_by_national_id(self):
        def config_label():
            relative_label.grid_forget()
            tree_container.grid_forget()
            # label_content.grid(row = 3,column = 0,columnspan = 2 ,sticky = 'nsew',pady = 20)
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
            print(prisoners_data)
            relative_data = self.db.get_data_for_ralative_id(nationnal_id)
            print(relative_data)
            label_content.configure(text = f'ยินดีต้อนรับ\n{relative_data[1]}{relative_data[2]} {relative_data[3]}')
            
            button_reserve_now = ctk.CTkButton(button_frame,
                                                text='จองเยี่ยมทันที',
                                                font=('TH SarabunPSK', 32, 'bold'),
                                                command=lambda: reserve_now())
            button_reserve_future = ctk.CTkButton(button_frame,
                                                text='จองเยี่ยมล่วงหน้า',
                                                font=('TH SarabunPSK', 32, 'bold'),
                                                command=lambda: reserve_future())
            button_reserve_now.grid(row=1,column=0,sticky='nsew',padx=20,pady=10)
            button_reserve_future.grid(row=1,column=1,sticky='nsew',padx=20,pady=10)
            now = datetime.now()

            def reserve_now():
                button_frame.grid_forget()
                tree_container.grid(row=2,column=0,columnspan=2,sticky='nsew',padx=20,pady=10)

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
                    alert = ALERT(popup_reserve_to_visit,[f'ไม่พบข้อมูล \n {national_id_entry.get()}'],button=True)
                    national_id_entry.delete(0, 'end')
                    return
                for row in tree.get_children():
                    tree.delete(row)
                for index,row in enumerate(prisoners_data):
                    if row[4] not in allower_dan:
                        continue
                    tree.insert('','end',values=row)

                if len(tree.get_children()) == 0:
                    alert = ALERT(popup_reserve_to_visit,['ไม่พบข้อมูลผู้ต้องขังที่เยี่ยมได้\nกรุณาตรวจสอบวันและเวลาเยี่ยม'],button=False)
                    alert.after(3000,lambda: (alert.destroy(),config_label()))
                else:
                    relative_label.configure(text =f'กรุณากดเลือกเพื่อจองเยี่ยม' )
                    relative_label.grid(row=1,column=0,columnspan=2,sticky='nsew' )
                    tree.grid(row=1,column=0,columnspan=2,sticky='nsew')
                    tree_container.grid(row = 2,column=0,columnspan = 2,padx=20, pady=10, sticky="nsew")

            def reserve_future():
                print('จองเยี่ยมล่วงหน้า')# สร้าง tree ใหม่สำหรับจองล่วงหน้า
                future_tree_container = ctk.CTkFrame(popup_reserve_to_visit)
                future_tree_container.grid_rowconfigure(0, weight=1)
                future_tree_container.grid_columnconfigure(0, weight=1)
                future_tree_container.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

                # สร้าง treeview สำหรับจองล่วงหน้า
                future_tree = ttk.Treeview(
                    future_tree_container,
                    columns=('prisoner_id','f_name','l_name','level','dan','relation'),
                    show='headings',
                    height=10
                )

                future_tree.heading('prisoner_id',text='รหัสประจำตัว')
                future_tree.heading('f_name',text='ชื่อ')
                future_tree.heading('l_name',text='นามสกุล')
                future_tree.heading('level',text='ชั้น')
                future_tree.heading('dan',text='แดน')
                future_tree.heading('relation',text='ความสัมพันธ์')

                future_tree.column('prisoner_id')
                future_tree.column('f_name')
                future_tree.column('l_name')
                future_tree.column('level')
                future_tree.column('dan')
                future_tree.column('relation')

                future_scrollbar = ttk.Scrollbar(future_tree_container, orient='vertical', command=future_tree.yview)
                future_tree.configure(yscrollcommand=future_scrollbar.set)
                future_tree.grid(row=0, column=0, sticky='nsew')
                future_scrollbar.grid(row=0, column=1, sticky='ns')

                # ดึงข้อมูลผู้ต้องขังที่สามารถจองล่วงหน้าได้ (ตัวอย่าง: ใช้ prisoners_data เดิม)
                for row in future_tree.get_children():
                    future_tree.delete(row)
                for index, row in enumerate(prisoners_data):
                    # สามารถเพิ่มเงื่อนไขเฉพาะสำหรับจองล่วงหน้าได้ที่นี่
                    future_tree.insert('', 'end', values=row)

                
            return
            # --- เพิ่มส่วนนี้ ---
            now = datetime.now()
            show_for_next_day = False
            if now.hour > 14 or (now.hour == 14 and now.minute >= 0):
                # วันถัดไป
                tomorrow = now + timedelta(days=1)
                tomorrow_day = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์","อาทิตย์"][tomorrow.weekday()]
                allowed_dan_by_dan = {
                    "จันทร์" : ['6','รจช'],
                    "อังคาร" : ['5','รจช'],
                    "พุธ" : ['1','2','3','4','7','รจช'],
                    "พฤหัสบดี" : ['5','6','รจช'],
                    "ศุกร์" : ['1','2','3','4','7','รจช']        
                }
                allower_dan = allowed_dan_by_dan.get(tomorrow_day,[])
                show_for_next_day = True
            else:
                allowed_dan_by_dan = {
                    "จันทร์" : ['6','รจช'],
                    "อังคาร" : ['5','รจช'],
                    "พุธ" : ['1','2','3','4','7','รจช'],
                    "พฤหัสบดี" : ['5','6','รจช'],
                    "ศุกร์" : ['1','2','3','4','7','รจช']        
                }
                allower_dan = allowed_dan_by_dan.get(day,[])
            # --- จบส่วนเพิ่ม ---


            if prisoners_data != []:
                print(prisoners_data)
            else:
                alert = ALERT(popup_reserve_to_visit,[f'ไม่พบข้อมูล \n {national_id_entry.get()}'],button=True)
                national_id_entry.delete(0, 'end')
                return

            print(f'วันนี้ = {day}')
            for row in prisoners_data:
                print(f'ข้อมูลใน prisoner_data : {row}')
            for row in tree.get_children():
                tree.delete(row)

            for index,row in enumerate(prisoners_data):
                if row[4] not in allower_dan:
                    continue
                tree.insert('','end',values=row)

            if len(tree.get_children()) == 0:
                if show_for_next_day:
                    alert = ALERT(popup_reserve_to_visit,['กรุณาตรวจสอบแดน\nก่อนจองล่วงหน้า'],button=False)
                else:
                    alert = ALERT(popup_reserve_to_visit,['ไม่พบข้อมูลผู้ต้องขังที่เยี่ยมได้\nกรุณาตรวจสอบวันและเวลาเยี่ยม'],button=False)
                alert.after(3000,lambda: (alert.destroy(),config_label()))
            else:
                relative_label.configure(text =f'กรุณากดเลือกเพื่อจองเยี่ยม' )
                relative_label.grid(row=1,column=0,columnspan=2,sticky='nsew' )
                tree.grid(row=1,column=0,columnspan=2,sticky='nsew')
                tree_container.grid(row = 2,column=0,columnspan = 2,padx=20, pady=10, sticky="nsew")

        def item_select(_):
            try:
                for i in tree.selection():
                    prisoner_data = tree.item(i)['values']
                    break
                if self.open_nextscreen_window is None or not self.open_nextscreen_window.winfo_exists():
                    self.open_nextscreen_window = open_next_screen(prisoner_data)
                else:
                    self.open_nextscreen_window.lift()
            except Exception as e:
                print(f'เกิดข้อผิดพลาด item_select(_) : {e}')

        def on_close(e = None):
            popup_reserve_to_visit.destroy()

        def can_reserve_for_next_day():
            now = datetime.now()
            if now.hour > 14 or (now.hour == 14 and now.minute >= 0):
                return True
            return False

        def get_next_reserve_date():
            # คืนค่าวันถัดไปในรูปแบบ YYYY-MM-DD
            return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        def open_next_screen(data):
            
            # ตรวจสอบว่าวันนี้ได้เยี่ยมแล้วหรือยัง psn_id คือ prisoner_id
            psn_id = data[0]
            psn_level = data[3]
            today = datetime.today().date().isoformat()
            today_month = datetime.today().strftime('%Y-%m')
            check_visit = self.db.get_count_visit(psn_id,today,today_month) # index 0 count_day index 1 coutn_month
            print(type(check_visit[1]))

            reserve_date = datetime.now().strftime("%Y-%m-%d")

            if can_reserve_for_next_day():
                reserve_date = get_next_reserve_date()

            if check_visit[0] > 0 :
                alert = ALERT(popup_reserve_to_visit,['กรุณาตรวจสอบข้อมูล\nผู้ต้องขังเยี่ยมได้ไม่เกิน 1 ครั้ง ต่อวัน'],button=False)
                alert.after(3000,lambda: (alert.destroy(),config_label()))
                return
            if psn_level == 'เยี่ยม' and check_visit[1] >= 8 :
                alert = ALERT(popup_reserve_to_visit,[f'กรุณาตรวจสอบข้อมูล\nชั้น {psn_level}\nเยี่ยมได้ไม่เกิน 8 ครั้ง ต่อเดือน'],button=False)
                alert.after(3000,lambda: (alert.destroy(),config_label()))
                return
            if psn_level == 'ดีมาก' and check_visit[1] >= 6 :
                alert = ALERT(popup_reserve_to_visit,[f'กรุณาตรวจสอบข้อมูล\nชั้น {psn_level}\nเยี่ยมได้ไม่เกิน 6 ครั้ง ต่อเดือน'],button=False)
                alert.after(3000,lambda: (alert.destroy(),config_label()))
                return
            if psn_level == 'ดี' and check_visit[1] >= 4 :
                alert = ALERT(popup_reserve_to_visit,[f'กรุณาตรวจสอบข้อมูล\nชั้น {psn_level}\nเยี่ยมได้ไม่เกิน 4 ครั้ง ต่อเดือน'],button=False)
                alert.after(3000,lambda: (alert.destroy(),config_label()))
                return
            if psn_level == 'กลาง' and check_visit[1] >= 3 :
                alert = ALERT(popup_reserve_to_visit,[f'กรุณาตรวจสอบข้อมูล\nชั้น {psn_level}\nเยี่ยมได้ไม่เกิน 3 ครั้ง ต่อเดือน'],button=False)
                alert.after(3000,lambda: (alert.destroy(),config_label()))
                return
            if psn_level == 'ระหว่างพิจารณาคดี' and check_visit[1] >= 3 :
                alert = ALERT(popup_reserve_to_visit,[f'กรุณาตรวจสอบข้อมูล\nชั้น {psn_level}\nเยี่ยมได้ไม่เกิน 3 ครั้ง ต่อเดือน'],button=False)
                alert.after(3000,lambda: (alert.destroy(),config_label()))
                return
            if psn_level == 'ปรับปรุง' and check_visit[1] >= 2 :
                alert = ALERT(popup_reserve_to_visit,[f'กรุณาตรวจสอบข้อมูล\nชั้น {psn_level}\nเยี่ยมได้ไม่เกิน 2 ครั้ง ต่อเดือน'],button=False)
                alert.after(3000,lambda: (alert.destroy(),config_label()))
                return
            if psn_level == 'ปรับปรุงมาก' and check_visit[1] >= 1 :
                alert = ALERT(popup_reserve_to_visit,[f'กรุณาตรวจสอบข้อมูล\nชั้น {psn_level}\nเยี่ยมได้ไม่เกิน 1 ครั้ง ต่อเดือน'],button=False)
                alert.after(3000,lambda: (alert.destroy(),config_label()))
                return


            relative_dict = {}
            data_relatives = self.db.get_relatives_id_fname_lname()
            for rel_id,f_name,l_name in data_relatives:
                full_name = f'{f_name} {l_name}'
                relative_dict[rel_id] = full_name

            next_screen = ctk.CTkToplevel(popup_reserve_to_visit)
            next_screen.geometry('400x750')
            next_screen.title('เลือกรอบเยี่ยม')
            next_screen.grab_set()
            next_screen.attributes('-topmost',True)
            next_screen.minsize(400,750)
            next_screen.maxsize(400,750)
            prisoner_id = data[0]
            # frame เลือกรอบ
            frame_select_round = ctk.CTkFrame(next_screen)
            # frame เลือกผู้ติดตาม
            frame_follower_visit = ctk.CTkFrame(next_screen)
            # frame ยืนยันการจอง
            frame_confirm_visit = ctk.CTkFrame(next_screen)

            round_visit_var = ctk.StringVar()
            follower_vars = []

            def next_screen_on_close():
                
                self.open_nextscreen_window = None
                tree_container.grid_forget()
                relative_label.grid_forget()
                next_screen.destroy()
                config_label()

            def select_round():
                for widget in frame_select_round.winfo_children():
                    widget.destroy()

                frame_follower_visit.pack_forget()
                frame_select_round.pack(fill='both', expand=True)

                label = ctk.CTkLabel(frame_select_round, text='เลือกรอบเยี่ยม', font=('TH SarabunPSK', 40, 'bold'))
                label.pack(pady=5)
                content = ctk.CTkLabel(frame_select_round, text=f'{data[1]} {data[2]}', font=('TH SarabunPSK', 30))
                content.pack(pady=5)

                now = datetime.now().time()
                late_time = datetime.strptime('14:00:00', "%H:%M:%S").time()

                if data[4] == 'รจช':
                    # 🔹 รอบเช้า (เวลาแสดง, เวลาเริ่มจริง, เวลาปิด)
                    rounds = [
                        ('เวลา 12.00 - 13.00', '12:00:00', '12:50:00')
                    ]
                    for text, start, close in rounds:
                        close_time = datetime.strptime(close, "%H:%M:%S").time()
                        if now < close_time:
                            ctk.CTkRadioButton(
                                frame_select_round,
                                text=text,
                                variable=round_visit_var,
                                value=start,
                                font=('TH SarabunPSK', 32, 'bold')
                            ).pack(pady=5)

                elif day == 'จันทร์' and str(data[4]) == '6':
                    # 🔹 รอบเช้า (เวลาแสดง, เวลาเริ่มจริง, เวลาปิด)
                    morning = MORING_ROUNDS()
                    ctk.CTkLabel(frame_select_round, text='รอบเช้า', font=('TH SarabunPSK', 32, 'bold')).pack(pady=10)
                    for text, start in morning.get_available_rounds(now, late_time):
                        ctk.CTkRadioButton(
                            frame_select_round,
                            text=text,
                            variable=round_visit_var,
                            value=start,
                            font=('TH SarabunPSK', 32, 'bold')
                        ).pack(pady=5)

                    # 🔹 รอบบ่าย
                    afternoon = AFTERNOON_ROUNDS()
                    ctk.CTkLabel(frame_select_round, text='รอบบ่าย', font=('TH SarabunPSK', 32, 'bold')).pack(pady=10)
                    for text, start in afternoon.get_available_rounds(now, late_time):
                        ctk.CTkRadioButton(
                            frame_select_round,
                            text=text,
                            variable=round_visit_var,
                            value=start,
                            font=('TH SarabunPSK', 32, 'bold')
                        ).pack(pady=5)                                                                                                          

                elif day == 'อังคาร' and str(data[4]) == '5':
                    # 🔹 รอบเช้า (เวลาแสดง, เวลาเริ่มจริง, เวลาปิด)
                    morning = MORING_ROUNDS()
                    ctk.CTkLabel(frame_select_round, text='รอบเช้า', font=('TH SarabunPSK', 32, 'bold')).pack(pady=10)
                    for text, start in morning.get_available_rounds(now, late_time):
                        ctk.CTkRadioButton(
                            frame_select_round,
                            text=text,
                            variable=round_visit_var,
                            value=start,
                            font=('TH SarabunPSK', 32, 'bold')
                        ).pack(pady=5)
                    
                    # 🔹 รอบบ่าย
                    afternoon = AFTERNOON_ROUNDS()
                    ctk.CTkLabel(frame_select_round, text='รอบบ่าย', font=('TH SarabunPSK', 32, 'bold')).pack(pady=10)
                    for text, start in afternoon.get_available_rounds(now, late_time):
                        ctk.CTkRadioButton(
                            frame_select_round,
                            text=text,
                            variable=round_visit_var,
                            value=start,
                            font=('TH SarabunPSK', 32, 'bold')
                        ).pack(pady=5) 

                elif day == 'พุธ' and str(data[4]) == '1':
                    # 🔹 รอบเช้า (เวลาแสดง, เวลาเริ่มจริง, เวลาปิด)
                    morning = MORING_ROUNDS()
                    ctk.CTkLabel(frame_select_round, text='รอบเช้า', font=('TH SarabunPSK', 32, 'bold')).pack(pady=10)
                    for text, start in morning.get_available_rounds(now, late_time):
                        ctk.CTkRadioButton(
                            frame_select_round,
                            text=text,
                            variable=round_visit_var,
                            value=start,
                            font=('TH SarabunPSK', 32, 'bold')
                        ).pack(pady=5)

                elif day == 'พุธ' and str(data[4]) in ['2','3','4','7']:                    
                    # 🔹 รอบบ่าย
                    afternoon = AFTERNOON_ROUNDS()
                    ctk.CTkLabel(frame_select_round, text='รอบบ่าย', font=('TH SarabunPSK', 32, 'bold')).pack(pady=10)
                    for text, start in afternoon.get_available_rounds(now, late_time):
                        ctk.CTkRadioButton(
                            frame_select_round,
                            text=text,
                            variable=round_visit_var,
                            value=start,
                            font=('TH SarabunPSK', 32, 'bold')
                        ).pack(pady=5) 

                elif day == 'พฤหัสบดี' and str(data[4]) == '5':
                    # 🔹 รอบเช้า (เวลาแสดง, เวลาเริ่มจริง, เวลาปิด)
                    morning = MORING_ROUNDS()
                    ctk.CTkLabel(frame_select_round, text='รอบเช้า', font=('TH SarabunPSK', 32, 'bold')).pack(pady=10)
                    for text, start in morning.get_available_rounds(now, late_time):
                        ctk.CTkRadioButton(
                            frame_select_round,
                            text=text,
                            variable=round_visit_var,
                            value=start,
                            font=('TH SarabunPSK', 32, 'bold')
                        ).pack(pady=5)
                elif day == 'พฤหัสบดี' and str(data[4]) == '6':
                    # 🔹 รอบบ่าย
                    afternoon = AFTERNOON_ROUNDS()
                    ctk.CTkLabel(frame_select_round, text='รอบบ่าย', font=('TH SarabunPSK', 32, 'bold')).pack(pady=10)
                    for text, start in afternoon.get_available_rounds(now, late_time):
                        ctk.CTkRadioButton(
                            frame_select_round,
                            text=text,
                            variable=round_visit_var,
                            value=start,
                            font=('TH SarabunPSK', 32, 'bold')
                        ).pack(pady=5)
                elif day == 'ศุกร์' and str(data[4]) == '1':
                    # 🔹 รอบเช้า (เวลาแสดง, เวลาเริ่มจริง, เวลาปิด)
                    morning = MORING_ROUNDS()
                    ctk.CTkLabel(frame_select_round, text='รอบเช้า', font=('TH SarabunPSK', 32, 'bold')).pack(pady=10)
                    for text, start in morning.get_available_rounds(now, late_time):
                        ctk.CTkRadioButton(
                            frame_select_round,
                            text=text,
                            variable=round_visit_var,
                            value=start,
                            font=('TH SarabunPSK', 32, 'bold')
                        ).pack(pady=5)

                elif day == 'ศุกร์' and str(data[4]) in ['2','3','4','7']:                    
                    # 🔹 รอบบ่าย
                    afternoon = AFTERNOON_ROUNDS()
                    ctk.CTkLabel(frame_select_round, text='รอบบ่าย', font=('TH SarabunPSK', 32, 'bold')).pack(pady=10)
                    for text, start in afternoon.get_available_rounds(now, late_time):
                        ctk.CTkRadioButton(
                            frame_select_round,
                            text=text,
                            variable=round_visit_var,
                            value=start,
                            font=('TH SarabunPSK', 32, 'bold')
                        ).pack(pady=5)
                
                # 🔸 ปุ่ม
                submit = ctk.CTkButton(
                    frame_select_round,
                    text='เลือกผู้ติดตาม',
                    command=lambda: select_follower() if round_visit_var.get() else ALERT(frame_select_round, msg=['\nกรุณาเลือกรอบเยี่ยม']),
                    font=('TH SarabunPSK', 24, 'bold'),
                    height=100
                )

                cancel = ctk.CTkButton(
                    frame_select_round,
                    text='ยกเลิก',
                    command=next_screen_on_close,
                    font=('TH SarabunPSK', 24, 'bold'),
                    height=40,
                    fg_color='red'
                )

                cancel.pack(side='bottom', pady=10)
                submit.pack(side='bottom', pady=10)

            def select_follower():
                for widget in frame_follower_visit.winfo_children():
                    widget.destroy()
                frame_select_round.pack_forget()
                frame_confirm_visit.pack_forget()

                # date time จากการเลือกรอบเยี่ยม
                round_time = round_visit_var.get()
                round_time_strtime = (datetime.strptime(round_time,"%H:%M:%S")).strftime("%H:%M:%S")
                count_visit = self.db.get_count_visit_on_round(round_time,reserve_date)
                
                print(f'count_visit = {count_visit}')

                if count_visit > 14:
                    count_alert = ALERT(next_screen,['รอบเต็ม\nกรุณาเลือกรอบใหม่'],text_color='red',button=True)
                    select_round()
                    return
                                          
                frame_follower_visit.pack(fill = 'both',expand = True)
                text_from_round = f'จองเยี่ยม\n{data[1]} {data[2]}\nเยี่ยมเวลา {round_visit_var.get()} น.'
                ctk.CTkLabel(frame_follower_visit,text=text_from_round,font=('TH SarabunPSK',28)).pack(pady = 10)


                followers = self.db.get_join_prisoners_and_relatives_not_follower(prisoner_id,nationnal_id)
                ctk.CTkLabel(frame_follower_visit,text='กรุณาเลือกผู้ติดตาม',font=('TH SarabunPSK',32,'bold')).pack(pady = 10)
                ctk.CTkLabel(frame_follower_visit,text='(เลือกผู้ติดตามได้สูงสุด 4 คน)',text_color='red',font=('TH SarabunPSK',24,'bold')).pack(pady = 10)
                if followers:
                    for follower in followers:
                        rid,title,fname,lname = follower
                        var = ctk.BooleanVar()
                        chk = ctk.CTkCheckBox(frame_follower_visit,
                                              text=f'{title}{fname} {lname}',
                                              variable=var,
                                              font=('TH SarabunPSK',28,'bold'))
                        chk.pack(pady = 5,padx = 50,anchor = 'nw')
                        follower_vars.append((rid,var))
                else:
                    ctk.CTkLabel(frame_follower_visit,text='ไม่มีผู้ติดตาม',font=('TH SarabunPSK',28,'bold')).pack(pady = 10)

                submit = ctk.CTkButton(frame_follower_visit,
                                    text='ถัดไป',
                                    command=lambda:confirm_visit(round_time_strtime,reserve_date),
                                    font=('TH SarabunPSK',24,'bold'),
                                    height=100
                                    )
                
                cancel = ctk.CTkButton(frame_follower_visit,
                                    text='ย้อนกลับ',
                                    command=lambda:select_round(),
                                    font=('TH SarabunPSK',24,'bold'),
                                    height=40,
                                    fg_color='orange'
                                    )
                cancel.pack(side = 'bottom',pady = 10)
                submit.pack(side = 'bottom',pady = 10)

            def confirm_visit(round_time_strtime,reserve_date):
                for widget in frame_confirm_visit.winfo_children():
                    widget.destroy()

                frame_follower_visit.pack_forget()
                frame_confirm_visit.pack(fill = 'both',expand = True)
                ctk.CTkLabel(frame_confirm_visit,text='กรุณาตรวจสอบข้อมูลให้ถูกต้อง',font=('TH SarabunPSK',24,'bold')).pack(pady = 20)
                select_fl_id = [rid for rid,var in follower_vars if var.get()]
                prepare_data = [reserve_date,round_time_strtime,prisoner_id,nationnal_id]

                ctk.CTkLabel(frame_confirm_visit,text=f'จองเยี่ยม\n{data[1]} {data[2]}\nเวลา {round_visit_var.get()} น.\nโดย {relative_dict.get(nationnal_id)}\nผู้ติดตาม',font=('TH SarabunPSK',28)).pack(pady = 5)
                for index,row in enumerate(select_fl_id):
                    prepare_data.append(row)
                    ctk.CTkLabel(frame_confirm_visit,text=f'คนที่ {index +1} {relative_dict.get(row)}',font=('TH SarabunPSK',28)).pack(pady = 5)

                select_fl_id.clear()

                if len(prepare_data) > 8:
                    print(f'ใน if = {prepare_data}')
                    prepare_data.clear()
                    follower_vars.clear()
                    select_follower()
                    alert = ALERT(frame_follower_visit,msg=['เลือกผู้ติดตามได้ไม่เกิน 4 คน','กรุณาเลือกใหม่'])
                
                submit = ctk.CTkButton(frame_confirm_visit,
                                    text='ยืนยันการจองเยี่ยม',
                                    command=lambda:insert_reserve_visit_to_db(prepare_data),
                                    font=('TH SarabunPSK',24,'bold'),
                                    height=100
                                    )
            
                back = ctk.CTkButton(frame_confirm_visit,
                                    text='ย้อนกลับ',
                                    command=lambda:go_back() ,
                                    font=('TH SarabunPSK',24,'bold'),
                                    height=40,
                                    fg_color='orange'
                                    )
                cancel = ctk.CTkButton(frame_confirm_visit,
                                    text='ยกเลิกการจอง',
                                    command=lambda:next_screen_on_close(),
                                    font=('TH SarabunPSK',24,'bold'),
                                    height=40,
                                    fg_color='red'
                                    )
                cancel.pack(side = 'bottom',pady = 20)
                back.pack(side = 'bottom',pady = 20)
                submit.pack(side = 'bottom',pady = 20)

                def go_back():
                    prepare_data.clear()
                    follower_vars.clear()
                    select_follower()
                    
            def insert_reserve_visit_to_db(prepare_data):
                print(prepare_data)
                if len(prepare_data) == 8:
                    query = "INSERT INTO visits (date_visit,time_visit,prisoner_id,relative_id_1,relative_id_2,relative_id_3,relative_id_4,relative_id_5) VALUES (?,?,?,?,?,?,?,?)"
                    result = self.db.add_visits(query,prepare_data)
                    if result:
                        insert_succress()
                        return
                elif len(prepare_data) == 7:
                    query = "INSERT INTO visits (date_visit,time_visit,prisoner_id,relative_id_1,relative_id_2,relative_id_3,relative_id_4) VALUES (?,?,?,?,?,?,?)"
                    result = self.db.add_visits(query,prepare_data)
                    if result:
                        insert_succress()
                        return
                elif len(prepare_data) == 6:
                    query = "INSERT INTO visits (date_visit,time_visit,prisoner_id,relative_id_1,relative_id_2,relative_id_3) VALUES (?,?,?,?,?,?)"
                    result = self.db.add_visits(query,prepare_data)
                    if result:
                        insert_succress()
                        return
                elif len(prepare_data) == 5:
                    query = "INSERT INTO visits (date_visit,time_visit,prisoner_id,relative_id_1,relative_id_2) VALUES (?,?,?,?,?)"
                    result = self.db.add_visits(query,prepare_data)
                    if result:
                        insert_succress()
                        return
                elif len(prepare_data) == 4:
                    query = "INSERT INTO visits (date_visit,time_visit,prisoner_id,relative_id_1) VALUES (?,?,?,?)"
                    result = self.db.add_visits(query,prepare_data)
                    if result:
                        insert_succress()
                        return
                
            def insert_succress():
                alert = ALERT(next_screen,['จองเยี่ยมสำเร็จ'],button=True)
                result =alert.show()
                if result:
                    next_screen_on_close()
            
            select_round()
            next_screen.protocol("WM_DELETE_WINDOW", next_screen_on_close)
            return next_screen

        popup_reserve_to_visit = ctk.CTkToplevel(self) 
        popup_reserve_to_visit.title('จองเยี่ยม')
        popup_reserve_to_visit.geometry('980x520+1+1')
        popup_reserve_to_visit.grab_set()
        popup_reserve_to_visit.focus()
        popup_reserve_to_visit.grid_columnconfigure((0,1),weight=1,uniform='popup_reserve')
        popup_reserve_to_visit.grid_rowconfigure(1,weight=0,uniform='popup_reserve')
        insert_national_frame = ctk.CTkFrame(popup_reserve_to_visit)
        insert_national_frame.grid_rowconfigure(0,weight=1,uniform='popup_reserve')
        insert_national_frame.grid_columnconfigure((0,1,2),weight=1,uniform='popup_reserve')
        
        button_frame = ctk.CTkFrame(popup_reserve_to_visit)
        button_frame.grid_rowconfigure((0,1),weight=1,uniform='popup_reserve',minsize=150)
        button_frame.grid_columnconfigure((0,1),weight=1,uniform='popup_reserve')

        insert_label = ctk.CTkLabel(insert_national_frame,text='กรุณากรอกเลขบัตรประชาชน :',font=('TH SarabunPSK', 32, 'bold'))
        insert_label.grid(row=0,column=0,pady=10,sticky='e',padx = 10)
        btn_read_id = ctk.CTkButton(insert_national_frame,
                                    text='อ่านข้อมูล',
                                    font=('TH SarabunPSK', 32, 'bold'),
                                    command=lambda : get_relative(True))
        btn_read_id.grid(row=0,column=2,pady=10,sticky='w',padx = 10)
        label_content = ctk.CTkLabel(button_frame,text='ยินดีต้อนรับ',font=('TH SarabunPSK', 52, 'bold'))
        label_content.grid(row = 0,column = 0,columnspan = 3 ,sticky = 'nsew',pady = 20)
        national_id_entry = ctk.CTkEntry(insert_national_frame,font=('TH SarabunPSK', 32, 'bold'),placeholder_text='เลขบัตรประชาชน 13 หลัก',width=300)
        national_id_entry.grid(row=0,column=1,pady=10,sticky='ew',padx = 10)
        national_id_entry.bind('<Return>',lambda e: get_relative())
        national_id_entry.bind('<KP_Enter>',lambda e: get_relative())

        # label_content = ctk.CTkLabel(popup_reserve_to_visit,text='',font=('TH SarabunPSK', 52, 'bold'))
        date_label = ctk.CTkLabel(popup_reserve_to_visit,font=('TH SarabunPSK', 52, 'bold'))
        relative_label = ctk.CTkLabel(popup_reserve_to_visit,font=('TH SarabunPSK', 46, 'bold'))
        flag_status = False
        nationnal_id = None
        days = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์","อาทิตย์"]
        months = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน",
                    "พฤษภาคม","มิถุนายน","กรกฎาคม", "สิงหาคม",
                    "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]

        current_time = t.localtime()
        day = days[current_time.tm_wday]
        month = months[current_time.tm_mon - 1]

        tree_container = ctk.CTkFrame(popup_reserve_to_visit)
        tree_container.grid_rowconfigure(1,weight=1)
        tree_container.grid_columnconfigure(0,weight=1)
        config_label()
        # กำหนด style สำหรับ treeview 
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Treeview',font =('TH SarabunPSK',18),rowheight = 35)
        style.configure('Treeview.Heading',font = ('TH SarabunPSK',18,'bold'))

        tree = ttk.Treeview(tree_container,columns=('prisoner_id','f_name','l_name','level','dan','relation'),show='headings',height=10)
        tree.heading('prisoner_id',text='รหัสประจำตัว')
        tree.heading('f_name',text='ชื่อ')
        tree.heading('l_name',text='นามสกุล')
        tree.heading('level',text='ชั้น')
        tree.heading('dan',text='แดน')
        tree.heading('relation',text='ความสัมพันธ์')

        tree.column('prisoner_id')
        tree.column('f_name')
        tree.column('l_name')
        tree.column('level')
        tree.column('dan')
        tree.column('relation')

        scrollbar = ttk.Scrollbar(tree_container,orient='vertical',command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        # เพิ่มปุ่มด้านล่าง tree
        btn_add = ctk.CTkButton(tree_container, text="เพิ่มข้อมูล", font=('TH SarabunPSK', 18, 'bold'), command=lambda: print("เพิ่มข้อมูล"))
        btn_add.grid(row=1, column=0, pady=10, sticky='ew')

        btn_edit = ctk.CTkButton(tree_container, text="แก้ไขข้อมูล", font=('TH SarabunPSK', 18, 'bold'), command=lambda: print("แก้ไขข้อมูล"))
        btn_edit.grid(row=2, column=0, pady=10, sticky='ew')

        btn_delete = ctk.CTkButton(tree_container, text="ลบข้อมูล", font=('TH SarabunPSK', 18, 'bold'), fg_color='red', command=lambda: print("ลบข้อมูล"))
        btn_delete.grid(row=3, column=0, pady=10, sticky='ew')

        tree.bind('<<TreeviewSelect>>',item_select)

        popup_reserve_to_visit.protocol("WM_DELETE_WINDOW", on_close)

##############################################################################################################################################################################
    # รายงานการเยี่ยม
##############################################################################################################################################################################
    def report_visits(self):

        def resize_tree_column():
            tree_container.update_idletasks()
            total_width = tree_container.winfo_width()
            for col, ratio in column_ratios.items():
                tree.column(col,width=int(total_width * ratio),anchor='w')

        def print_table():
            try:

                # สร้าง pdf
                temp_pdf = tempfile.mktemp(".pdf")
                c = canvas.Canvas(temp_pdf,pagesize=landscape(A4))
                width,height = landscape(A4)
                
                # ฟรอน และ ระยะห่าง
                c.setFont("TH SarabunPSK", 18)
                c.drawCentredString(width / 2, height - 1.5 * cm, f"รายงานการเยี่ยม วันที่ {date_now} เวลาเยี่ยม {combo_round.get()}")
                c.setFont("TH SarabunPSK", 11)

                # หัวตารางและความกว้าง
                columns = tree["columns"]
                # col_widths = [ (width -4*cm) / len(columns)] * len(columns)
                # headers = [tree.heading(col)["text"] for col in columns]
                col_widths = [3.07*cm] * len(columns)
                headers = [tree.heading(col)["text"] for col in columns]

                # ตำแหน่งเริ่ม
                start_x = 1*cm
                start_y = height -3 * cm
                row_height = 0.8*cm

                # วาดหัวตาราง
                y = start_y
                x = start_x
                for i,header in enumerate(headers):
                    c.rect(x,y,col_widths[i],row_height,stroke=1,fill=0)
                    c.drawString(x+0.2*cm,y+0.3*cm,header)
                    x += col_widths[i]
                
                # วาดข้อมูล
                y -= row_height
                for child_id in tree.get_children():
                    x = start_x
                    values = tree.item(child_id,"values")
                    for i,value in enumerate(values):
                        c.rect(x,y,col_widths[i],row_height,stroke=1,fill=0)
                        text = str(value)

                        # จัดชิดขวาถ้าเป็นตัวเลข
                        if text.isdigit():
                            text_width = c.stringWidth(text,"TH SarabunPSK",10)
                            c.drawString(x+col_widths[i]-text_width-0.2*cm,y+0.3*cm,text)
                        else:
                            c.drawString(x+0.2*cm,y+0.3*cm,text)
                        x += col_widths[i]
                    y -= row_height
                c.save()
                
                # สั่งพิมพ์
                os.startfile(temp_pdf)
                messagebox.showinfo('กำลังพิมพ์','สั่งพิมพ์เรียบร้อย')

            except Exception as e:
                messagebox.showerror('ข้อผิดพลาด',f'ไม่สามารถพิมพ์ได้ :\n{e}')

        def get_visits():
            tree.grid_forget()
            round_time = combo_round.get()
            year = year_var.get()
            month = month_dict[month_var.get()]
            day = day_var.get()
            round_date = f"{year}-{month}-{day}"
            print(f'round_date = {round_date}')
            data = [round_date, round_time]
            result = self.db.get_visits(data)
            for row in tree.get_children():
                tree.delete(row)
            for row in result:
                tree.insert('','end',values=row)
            tree_container.grid(row = 2 ,column = 0 ,columnspan = 6)
            tree.grid(row=0)
            button_print = ctk.CTkButton(self.popup_report_visits,text='พิมพ์',command=lambda:print_table())
            button_print.grid(row= 3,column = 0 ,columnspan = 3 ,pady = 20)


        def on_right_click(event):
            nonlocal popup_window_right_click
            selected = tree.identify_row(event.y)
            if not selected:
                return
            values = tree.item(selected)['values']
            # for i in values:
            #     print(i)
            # ฟังก์ชันสำหรับเมนูคลิกขวา
            def move_round():

                def move_round():
                    round_selected = time_visit.get()
                    print(date_current)
                    print(f'move round {round_selected}')
                    result_count_round_visit = self.db.get_count_visit_on_round(round_selected,date_current)
                    print(f'จำนวนคนที่จองรอบ {result_count_round_visit}')
                    if result_count_round_visit >=15:
                        alert = ALERT(move_round_pupup,['รอบเต็ม\nกรุณาเลือกรอบใหม่'],text_color='red',button=True)
                        alert.after(3000,lambda: (alert.destroy(),move_round_pupup.destroy()))
                        return
                    else:
                        result_move_round = self.db.update_visit_round(round_selected,values[0])
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
                move_round_pupup.title('ย้ายรอบเยี่ยม')
                move_round_pupup.geometry('500x200+400+50')
                move_round_pupup.grab_set()
                move_round_pupup.focus()

                move_round_pupup.grid_columnconfigure(0,weight=1,uniform='move_round')
                move_round_pupup.grid_rowconfigure((0,1,2),weight=1,uniform='move_round')
                label_content = ctk.CTkLabel(move_round_pupup,text=f'ย้ายรอบเยี่ยม\n{values[4]}',font=('TH SarabunPSK',32,'bold'))
                label_content.grid(row = 0 , column = 0 ,sticky = 'ns')
                time_visit = ctk.CTkOptionMenu(move_round_pupup,
                                                values=['09:30:00','10:00:00','10:30:00','11:00:00','13:15:00','13:45:00','14:15:00'],
                                                font=('TH SarabunPSK',18),
                                                dropdown_font=('TH SarabunPSK',18))
                time_visit.grid(row=1,column=0,sticky='ns',padx = 40,pady = 20)
                button = ctk.CTkButton(move_round_pupup,text='ยืนยัน',width=140,font=('TH SarabunPSK',18),command=lambda: move_round())
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
                
                def check_label_visit(data_visit_label,btn):
                    all_label = list()
                    all_label.append(data_visit_no_1.cget('text'))
                    all_label.append(data_visit_no_2.cget('text'))
                    all_label.append(data_visit_no_3.cget('text'))
                    all_label.append(data_visit_no_4.cget('text'))
                    all_label.append(data_visit_no_5.cget('text'))

                    relative_id = read_card()
                    result_visit = self.db.prisoner_id_on_table_visits(values[0])
                    result_count = self.db.count_relative(result_visit,relative_id)

                    if result_count == 0:
                        alert = ALERT(add_visit_popup,msg=['ไม่พบข้อมูลและความสัมพันธ์'],button=True)
                        return
                    for i in all_label:
                        print(i,relative_id)
                        if i == relative_id:
                            alert = ALERT(add_visit_popup,msg=[f'หมายเลข {relative_id}\nมีการจองเยี่ยมแล้ว'],button=True)
                            return
                    
                    data_visit_label.configure(text = relative_id)
                    label = data_visit_label.cget('text')
                    if label == '' or label == None:
                        print('label == '' or none')
                        return
                    btn = btn
                    btn.grid_forget()
                    return
                
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
                add_visit_popup.title('เพิ่มชื่อญาติเยี่ยม')
                add_visit_popup.geometry('480x720+400+50')  
                add_visit_popup.grab_set()
                add_visit_popup.focus()

                add_visit_popup.grid_columnconfigure((0,1),weight=1,uniform='add_visit')
                add_visit_popup.grid_rowconfigure((0,1,2,3,4,5,6,7,8),weight=1,uniform='add_visit')
                label_content = ctk.CTkLabel(add_visit_popup,text=f'เพิ่มชื่อญาติเยี่ยม\n{values[3]} น.  {values[4]}',font=('TH SarabunPSK',32,'bold'))
                label_content.grid(row = 0 , column = 0 , columnspan = 2,sticky = 'ns')
                date_label = ctk.CTkLabel(add_visit_popup,text=f'วันที่จอง {values[2]}',font=('TH SarabunPSK',24))
                date_label.grid(row = 1 , column = 0 , columnspan = 2,sticky = 'ns')   
                time_label = ctk.CTkLabel(add_visit_popup,text=f'เวลาเยี่ยม {values[3]} น.',font=('TH SarabunPSK',24))
                time_label.grid(row = 2 , column = 0 , columnspan = 2,sticky = 'ns')
                visit_no_1 = ctk.CTkLabel(add_visit_popup,text='ญาติคนที่ 1 :',font=('TH SarabunPSK',24))
                visit_no_1.grid(row = 3 , column = 0 , sticky = 'e',padx = 20,pady = 10)   
                visit_no_2 = ctk.CTkLabel(add_visit_popup,text='ญาติคนที่ 2 :',font=('TH SarabunPSK',24))    
                visit_no_2.grid(row = 4 , column = 0 , sticky = 'e',padx = 20,pady = 10)
                visit_no_3 = ctk.CTkLabel(add_visit_popup,text='ญาติคนที่ 3 :',font=('TH SarabunPSK',24))
                visit_no_3.grid(row = 5 , column = 0 , sticky = 'e',padx = 20,pady = 10)
                visit_no_4 = ctk.CTkLabel(add_visit_popup,text='ญาติคนที่ 4 :',font=('TH SarabunPSK',24))
                visit_no_4.grid(row = 6 , column = 0 , sticky = 'e',padx = 20,pady = 10)
                visit_no_5 = ctk.CTkLabel(add_visit_popup,text='ญาติคนที่ 5 :',font=('TH SarabunPSK',24))
                visit_no_5.grid(row = 7 , column = 0 , sticky = 'e',padx = 20,pady = 10)

                data_visit_no_1 = ctk.CTkLabel(add_visit_popup,text='',font=('TH SarabunPSK',24))
                data_visit_no_1.grid(row = 3 , column = 1 , sticky = 'w',padx = 20,pady = 10)
                data_visit_no_2 = ctk.CTkLabel(add_visit_popup,text='',font=('TH SarabunPSK',24))
                data_visit_no_2.grid(row = 4 , column = 1 , sticky = 'w',padx = 20,pady = 10)
                data_visit_no_3 = ctk.CTkLabel(add_visit_popup,text='',font=('TH SarabunPSK',24))
                data_visit_no_3.grid(row = 5 , column = 1 , sticky = 'w',padx = 20,pady = 10)
                data_visit_no_4 = ctk.CTkLabel(add_visit_popup,text='',font=('TH SarabunPSK',24))
                data_visit_no_4.grid(row = 6 , column = 1 , sticky = 'w',padx = 20,pady = 10)
                data_visit_no_5 = ctk.CTkLabel(add_visit_popup,text='',font=('TH SarabunPSK',24))
                data_visit_no_5.grid(row = 7 , column = 1 , sticky = 'w',padx = 20,pady = 10)

                button_add_visit = ctk.CTkButton(add_visit_popup,text='เพิ่ม',font=('TH SarabunPSK',24),command=save_to_db)
                button_add_visit.grid(row = 8 , column = 0 ,padx = 20,pady = 10)
                button_cancel = ctk.CTkButton(add_visit_popup,text='ยกเลิก',fg_color='red',font=('TH SarabunPSK',24),command=lambda:add_visit_popup.destroy())
                button_cancel.grid(row = 8 , column = 1 ,padx = 20,pady = 10)

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
            
                if data_visit_no_1.cget('text') == '':
                    btn1 = ctk.CTkButton(add_visit_popup,text='เพิ่มญาติ',font=('TH SarabunPSK',24),command=lambda:check_label_visit(data_visit_no_1,btn1))
                    btn1.grid(row = 3 , column = 1 , sticky = 'w',padx = 20,pady = 10)
                if data_visit_no_2.cget('text') == '':
                    btn2 = ctk.CTkButton(add_visit_popup,text='เพิ่มญาติ',font=('TH SarabunPSK',24),command=lambda:check_label_visit(data_visit_no_2,btn2))
                    btn2.grid(row = 4 , column = 1 , sticky = 'w',padx = 20,pady = 10)
                if data_visit_no_3.cget('text') == '':
                    btn3 = ctk.CTkButton(add_visit_popup,text='เพิ่มญาติ',font=('TH SarabunPSK',24),command=lambda:check_label_visit(data_visit_no_3,btn3))
                    btn3.grid(row = 5 , column = 1 , sticky = 'w',padx = 20,pady = 10)
                if data_visit_no_4.cget('text') == '':
                    btn4 = ctk.CTkButton(add_visit_popup,text='เพิ่มญาติ',font=('TH SarabunPSK',24),command=lambda:check_label_visit(data_visit_no_4,btn4))
                    btn4.grid(row = 6 , column = 1 , sticky = 'w',padx = 20,pady = 10)
                if data_visit_no_5.cget('text') == '':
                    btn5 = ctk.CTkButton(add_visit_popup,text='เพิ่มญาติ',font=('TH SarabunPSK',24),command=lambda:check_label_visit(data_visit_no_5,btn5))
                    btn5.grid(row = 7 , column = 1 , sticky = 'w',padx = 20,pady = 10)

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
            popup_window_right_click.overrideredirect(True)
            popup_window_right_click.geometry(f'+{event.x_root}+{event.y_root}')
            popup_window_right_click.configure(fg_color = '#f0f0f0')

            ctk.CTkButton(popup_window_right_click,text='เพิ่มชื่อญาติเยี่ยม',font =('TH SarabunPSK',18,'bold'),command=add_visit,width=160).pack(padx = 10,pady = (10,5))
            ctk.CTkButton(popup_window_right_click,text='ย้ายรอบ',font =('TH SarabunPSK',18,'bold'),command=move_round,width=160).pack(padx = 10,pady = (10,5))
            ctk.CTkButton(popup_window_right_click,text='ยกเลิกรอบ',font=('TH SarabunPSK',18,'bold'),command=remove_round,width=160,fg_color='red').pack(padx = 10,pady = (10,5))
            
            popup_window_right_click.after(100, lambda: popup_window_right_click.focus_force())
            popup_window_right_click.bind('<FocusOut>',lambda e:popup_window_right_click.destroy())
        
        self.popup_report_visits.grid_columnconfigure((0,5),weight=1,uniform='popup_report_visits')
       

        date_now = datetime.now().strftime("%d/%m/%Y")
        # สร้างตัวเลือกปี เดือน วัน ด้วย ctk
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

        combo_year = ctk.CTkComboBox(self.popup_report_visits, values=years, variable=year_var, width=80, font=('TH SarabunPSK', 18),dropdown_font=('TH SarabunPSK', 18))
        combo_month = ctk.CTkComboBox(self.popup_report_visits, values=months_th, variable=month_var, width=120, font=('TH SarabunPSK', 18),dropdown_font=('TH SarabunPSK', 18))
        combo_day = ctk.CTkComboBox(self.popup_report_visits, values=days_in_month, variable=day_var, width=60, font=('TH SarabunPSK', 18),dropdown_font=('TH SarabunPSK', 18))

        combo_year.grid(row=1, column=1, padx=5, pady=20)
        combo_month.grid(row=1, column=2, padx=5, pady=20)
        combo_day.grid(row=1, column=3, padx=5, pady=20)

        date_current = datetime.now().strftime("%Y-%m-%d")
        label_content = ctk.CTkLabel(self.popup_report_visits,text=f'รายงานการเยี่ยม ประจำวันที่ {date_now}',font=('TH SarabunPSK',32,'bold'))
        label_content.grid(row = 0 , column = 0 , columnspan = 6 ,sticky = 'ns')

        label_select_round = ctk.CTkLabel(self.popup_report_visits,text='เลือกรอบเยี่ยม',font=('TH SarabunPSK',32,'bold'))
        label_select_round.grid(row = 1,column = 0,sticky = 'e')

        combo_round = ctk.CTkOptionMenu(self.popup_report_visits,values=['09:30:00','10:00:00','10:30:00','11:00:00','12:00:00','13:15:00','13:45:00','14:15:00'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
        combo_round.grid(row= 1,column = 4, sticky = 'ew',padx = 40,pady = 20)

        button = ctk.CTkButton(self.popup_report_visits,text='ค้นหา',font=('TH SarabunPSK',18),command=lambda:get_visits())
        button.grid(row = 1,column = 5 ,sticky = 'w')

        tree_container = ctk.CTkFrame(self.popup_report_visits)
        tree_container.grid_columnconfigure(0,weight=1)
        tree_container.grid_rowconfigure(1,weight=1)

        # กำหนด style สำหรับ treeview 
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Treeview',font =('TH SarabunPSK',16),rowheight = 35)
        style.configure('Treeview.Heading',font = ('TH SarabunPSK',16,'bold'))
        
        tree  = ttk.Treeview(tree_container,columns=('visit_id','time_stamp','date_visit','time_visit','prisoner_id','relation_id_1','relation_id_2','relation_id_3','relation_id_4','relation_id_5'),show='headings',height=10)

        tree.heading('time_stamp',text='Time Stamp')
        tree.heading('date_visit',text='วันที่จอง')
        tree.heading('time_visit',text='เวลาเยี่ยม')
        tree.heading('prisoner_id',text='ชื่อ')
        tree.heading('relation_id_1',text='ญาติคนที่ 1')
        tree.heading('relation_id_2',text='ญาติคนที่ 2')
        tree.heading('relation_id_3',text='ญาติคนที่ 3')
        tree.heading('relation_id_4',text='ญาติคนที่ 4')
        tree.heading('relation_id_5',text='ญาติคนที่ 5')

        tree.column('time_stamp')
        tree.column('date_visit')
        tree.column('time_visit')
        tree.column('prisoner_id')
        tree.column('relation_id_1')
        tree.column('relation_id_2')
        tree.column('relation_id_3')
        tree.column('relation_id_4')
        tree.column('relation_id_5')
        tree.column('visit_id',width=0,stretch=False)

        scrollbar = ttk.Scrollbar(tree_container,orient='vertical',command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # กำหนดความกว้าง column
        column_ratios = {
            'time_stamp' : 0.12,
            'date_visit' : 0.10,
            'time_visit' : 0.08,
            'prisoner_id' : 0.15,
            'relation_id_1' : 0.11,
            'relation_id_2' : 0.11,
            'relation_id_3' : 0.11,
            'relation_id_4' : 0.11,
            'relation_id_5' : 0.11
        }

        tree_container.bind('<Configure>',lambda e: resize_tree_column())
        tree.bind('<Button-3>',on_right_click)
        popup_window_right_click = None


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
            self.reserve_to_visit()
        elif page_name == 'ลงทะเบียนลายนิ้วมือ':
            print(page_name)
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