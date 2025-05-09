import customtkinter as ctk
import tkinter as tk
from tkinter import ttk,messagebox
from manage.database import SQLiteDB
import emoji
from pyzkfp import ZKFP2
import threading
import time as t
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import os
import tempfile



class MainFrame(ctk.CTkFrame):
    def __init__(self,parent):
        super().__init__(parent,bg_color='#D7F197')

        self.grid(row=0,column=1,sticky='nsew')
        self.db = SQLiteDB()
        self.zkfp2 = ZKFP2()

        # สร้าง Frame ลงทะเบียนผู้ต้องขัง #
        self.register_frame = ctk.CTkFrame(self)

        # สร้าง Frame เมนูค้นหาผู้ต้องขังเพือจัดการญาติ #
        self.showdata_frame = ctk.CTkFrame(self)

        # สร้าง Frame แสดงข้อมูลผู้ต้องขังทั้งหมดเป็นตาราง #
        self.show_all_prisoner_frame = ctk.CTkFrame(self)

        # สร้าง Frame สำหรับรายงานประวัติการเยี่ยมญาติ
        self.popup_report_visits = ctk.CTkFrame(self) 

        # ใช้ตรวจสอบการป้อนตัวเลขใน regis_entry_id
        self.vcmd = self.register(self.validate_number_input)
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
        self.register_frame.grid_rowconfigure((0,1,2,3,4,5,6,7,8),weight=1,uniform="register_frame")
        
        progressbar = ctk.CTkProgressBar(self.register_frame,mode='indeterminate')

        regis_label_content = ctk.CTkLabel(self.register_frame,text='ลงทะเบียนผู้ต้องขัง',font=('TH SarabunPSK',40,'bold'))
        regis_label_content.grid(row = 0,column = 0,columnspan = 2,sticky = 'nsew' , pady = 10)

        regis_label_id = ctk.CTkLabel(self.register_frame,text='รหัสประจำตัว : ',font=('TH SarabunPSK',18,'bold'),width=200,anchor='e')
        regis_label_id.grid(row = 1,column = 0,sticky = 'e',padx = 5)
        regis_entry_id = ctk.CTkEntry(self.register_frame,font=('TH SarabunPSK',18),width=200,validate='key',validatecommand = (self.vcmd,'%P'))
        regis_entry_id.grid(row = 1,column = 1,sticky = 'w',padx = 5)

        regis_label_sex = ctk.CTkLabel(self.register_frame,text='เพศ : ',font=('TH SarabunPSK',18,'bold'))
        regis_label_sex.grid(row = 2,column = 0,sticky = 'e',padx = 5)
        regis_combo_sex = ctk.CTkOptionMenu(self.register_frame,values=['','ชาย','หญิง'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
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
        regis_entry_lawsuit = ctk.CTkEntry(self.register_frame,font=('TH SarabunPSK',18),width=200)
        regis_entry_lawsuit.grid(row = 5,column = 1 ,sticky = 'w',padx = 5)

        regis_label_level = ctk.CTkLabel(self.register_frame,text='ชั้น : ',font=('TH SarabunPSK',18,'bold'))
        regis_label_level.grid(row = 6 ,column = 0,sticky = 'e',padx = 5)
        regis_combo_level = ctk.CTkOptionMenu(self.register_frame,values=['','ระหว่างพิจารณาคดี','เยี่ยม','ดีมาก','ดี','กลาง','ปรับปรุง','ปรับปรุงมาก'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
        regis_combo_level.grid(row = 6 ,column = 1,sticky = 'w',padx = 5)

        regis_label_dan = ctk.CTkLabel(self.register_frame,text='แดน : ',font=('TH SarabunPSK',18,'bold'))
        regis_label_dan.grid(row = 7,column = 0,sticky = 'e',padx = 5)
        regis_combo_dan = ctk.CTkOptionMenu(self.register_frame,values=['','1','2','3','4','5','6','7'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
        regis_combo_dan.grid(row = 7,column = 1,sticky = 'w',padx = 5)

        regis_button_submit = ctk.CTkButton(self.register_frame,
                                           text='บันทึกข้อมูล',
                                           width=100,
                                           font=('TH SarabunPSK',18,'bold'),
                                           command=lambda:save_data_to_db())
        regis_button_submit.grid(row = 8,column = 0,sticky = 'e',padx = 5)
        regis_button_clear = ctk.CTkButton(self.register_frame,
                                          text='ล้างข้อมูล',
                                          width=100,
                                          font=('TH SarabunPSK',18,'bold'),
                                          command=lambda:clear_data())
        regis_button_clear.grid(row = 8,column = 1,sticky = 'w',padx = 5)

        self.register_frame.grid_columnconfigure((0,1),minsize=300)

        # ล้างข้อมูลในช่องกรอกข้อมูล
        def clear_data():
            regis_entry_id.delete(0,ctk.END)
            regis_combo_sex.set(value='')
            regis_entry_name.delete(0,ctk.END)
            regis_entry_lname.delete(0,ctk.END)
            regis_entry_lawsuit.delete(0,ctk.END)
            regis_combo_level.set(value='')
            regis_combo_dan.set(value='')

        # ส่งข้อมูลไป Database
        def save_data_to_db():
            print('1')
            data = [regis_entry_id.get().strip(),
                    regis_combo_sex.get().strip(),
                    regis_entry_name.get().strip(),
                    regis_entry_lname.get().strip(),
                    regis_entry_lawsuit.get().strip(),
                    regis_combo_level.get().strip(),
                    regis_combo_dan.get().strip()]
            regis_button_submit.grid_forget()
            regis_button_clear.grid_forget()
            print('2')
            progressbar.grid(row = 8,column = 0,columnspan = 2,sticky = 'n',padx = 5)
            print('3')
            progressbar.start()
            print('4')
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
                messagebox.showerror('แจ้งการบันทึกข้อมูล','ไม่สามารถบันทึกข้อมูลได้กรุณาตรวจสอบใหม่')
                print('7')
                progressbar.stop
                progressbar.grid_forget()
                print('8')
                regis_button_submit.grid(row = 8,column = 0,sticky = 'e',padx = 5)
                regis_button_clear.grid(row = 8,column = 1,sticky = 'w',padx = 5)
                print('9')
                clear_data()

##############################################################################################################################################################################
#   ค้นหาผู้ต้องขังรายบุคคล
##############################################################################################################################################################################
    def search_one_prisoner(self):

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
        showdata_search_frame.grid(row = 3,column = 0,columnspan = 2,rowspan = 8,sticky = 'nsew')
        showdata_search_frame.grid_columnconfigure((0,1),weight=1)
        showdata_search_frame.grid_rowconfigure((0,1,2,3,4,5,6,7),weight=1)

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

        showdata_button_submit = ctk.CTkButton(showdata_search_frame,
                                                    text='เพิ่มญาติ',
                                                    width=100,
                                                    font=('TH SarabunPSK',18,'bold'),
                                                    command=lambda:register_relative())
        showdata_button_submit.grid(row = 7,column = 0,sticky = 'e',padx = 5)

        showdata_button_clear = ctk.CTkButton(showdata_search_frame,
                                                   text='รายชื่อญาติ',
                                                   width=100,
                                                   font=('TH SarabunPSK',18,'bold'),
                                                   command=lambda:show_list_relative())
        showdata_button_clear.grid(row = 7,column = 1,sticky = 'w',padx = 5)
        self.showdata_frame.grid_columnconfigure((0,1),minsize=200)

        # แสดงข้อมูลจากการค้นหา 1 คน
        def show_one_prisoner():
            
            button_search.grid_forget()
            progressbar.grid(row = 2,column = 0,columnspan = 2)
            progressbar.start()
            nonlocal prisoner_id_in_search_one
            nonlocal prisoner_name_in_search_one
            prison_id = search_one_var.get().strip()
            result_search_one = self.db.get_data_one(prison_id)
            if result_search_one:
                showdata_id_data.configure(text = result_search_one[0])
                showdata_sex_data.configure(text = result_search_one[1])
                showdata_fname_data.configure(text = result_search_one[2])
                showdata_lname_data.configure(text = result_search_one[3])
                showdata_lawsuit_data.configure(text = result_search_one[4])
                showdata_level_data.configure(text = result_search_one[5])
                showdata_dan_data.configure(text = result_search_one[6])
                prisoner_id_in_search_one = result_search_one[0]
                prisoner_name_in_search_one = result_search_one[2] + ' ' + result_search_one[3]
                
            else:
                messagebox.showerror('แจ้งเตือน',f'ไม่พบค่า {prison_id} ในฐานข้อมูล')
                showdata_id_data.configure(text = '')
                showdata_sex_data.configure(text = '')
                showdata_fname_data.configure(text = '')
                showdata_lname_data.configure(text = '')
                showdata_lawsuit_data.configure(text = '')
                showdata_level_data.configure(text = '')
                showdata_dan_data.configure(text = '')
                
            progressbar.stop()
            progressbar.grid_forget()
            button_search.grid(row = 2,column = 0,columnspan = 2)

            # ลงทะเบียนญาติ
        def register_relative():
            # prisoner_id_in_search_one = showdata_id_data.cget('text')
            # prisoner_name_in_search_one = showdata_fname_data.cget('text') + ' ' + showdata_lname_data.cget('text')
            nonlocal prisoner_name_in_search_one
            nonlocal prisoner_id_in_search_one
            if prisoner_id_in_search_one == '':
                messagebox.showerror(title='ข้อผิดพลาด',message='ไม่พบข้อมูลผู้ต้องขัง')
            else:
                popup_register_relation = ctk.CTkToplevel(self)
                popup_register_relation.title('ลงทะเบียนญาติ')
                popup_register_relation.geometry('480x720+1+1')
                popup_register_relation.grab_set()

                f_name_var = ctk.StringVar()
                l_name_var = ctk.StringVar()
                address_var = ctk.StringVar()
                tel_var = ctk.StringVar()

                # ตั้งค่า column
                for i in range(4):
                    popup_register_relation.grid_columnconfigure(i,weight=1,uniform='popup')
                for i in range(10): 
                    popup_register_relation.grid_rowconfigure(i,weight=1,uniform='popup')

                popup_label_content =ctk.CTkLabel(popup_register_relation,text='ลงทะเบียนญาติ',font=('TH SarabunPSK',28,'bold'))
                popup_label_content.grid(row = 0,column =0,columnspan = 4,pady = 5)

                popup_label_prisoner_id = ctk.CTkLabel(popup_register_relation,text='รหัสประจำตัว : ',font=('TH SarabunPSK',18,'bold'))
                popup_label_prisoner_id.grid(row = 1,column = 0,padx= 5,sticky = 'e')
                
                popup_label_prisoner_id_form_search_one = ctk.CTkLabel(popup_register_relation,text=prisoner_id_in_search_one,font=('TH SarabunPSK',18,'bold'))
                popup_label_prisoner_id_form_search_one.grid(row = 1,column = 1,padx= 5,sticky = 'w')

                popup_label_prisoner_name = ctk.CTkLabel(popup_register_relation,text='ชื่อ : ',font=('TH SarabunPSK',18,'bold'))
                popup_label_prisoner_name.grid(row = 1,column = 2,padx= 5,sticky = 'e')

                popup_label_prisoner_name_form_search_one = ctk.CTkLabel(popup_register_relation,text=prisoner_name_in_search_one,font=('TH SarabunPSK',18,'bold'))
                popup_label_prisoner_name_form_search_one.grid(row = 1,column = 3,padx= 5,sticky = 'w')

                popup_label_id_relative = ctk.CTkLabel(popup_register_relation,text='หมายเลขบัตรประชาชน',font=('TH SarabunPSK',18,'bold'))
                popup_label_id_relative.grid(row = 2,column = 0,columnspan = 2,padx= 5,sticky = 'e')

                popup_entry_id_relative = ctk.CTkEntry(popup_register_relation,font=('TH SarabunPSK',18),validate='key',validatecommand = (self.vcmd,'%P'))
                popup_entry_id_relative.grid(row = 2,column = 2,padx= 5,sticky = 'w')

                popup_button_check_id = ctk.CTkButton(popup_register_relation,
                                                      text='ตรวจสอบ',
                                                      width=100,
                                                      font=('TH SarabunPSK',18,'bold'),
                                                      command=lambda:check_relative_id())
                popup_button_check_id.grid(row=2 ,column = 3,padx= 5,sticky = 'w')

                popup_label_title_relative = ctk.CTkLabel(popup_register_relation,text='คำนำหน้า : ',font=('TH SarabunPSK',18,'bold'))
                popup_label_title_relative.grid(row = 3,column = 0,columnspan = 2,sticky = 'e',padx = 5)

                popup_combo_title_relative = ctk.CTkOptionMenu(popup_register_relation,values=['นาย','นาง','นางสาว'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
                popup_combo_title_relative.grid(row = 3,column = 2,columnspan = 2,sticky = 'w',padx = 5)

                popup_label_fname_relative = ctk.CTkLabel(popup_register_relation,text='ชื่อ : ',font=('TH SarabunPSK',18,'bold'))
                popup_label_fname_relative.grid(row = 4,column = 0,columnspan = 2,padx= 5,sticky = 'e')

                popup_entry_fname_relative = ctk.CTkEntry(popup_register_relation,font=('TH SarabunPSK',18),textvariable=f_name_var)
                popup_entry_fname_relative.grid(row = 4,column = 2,columnspan = 2,padx= 5,sticky = 'w')

                popup_label_lname_relative = ctk.CTkLabel(popup_register_relation,text='นามสกุล : ',font=('TH SarabunPSK',18,'bold'))
                popup_label_lname_relative.grid(row = 5,column = 0,columnspan = 2,padx= 5,sticky = 'e')

                popup_entry_lname_relative = ctk.CTkEntry(popup_register_relation,font=('TH SarabunPSK',18),textvariable=l_name_var,)
                popup_entry_lname_relative.grid(row = 5,column = 2,columnspan = 2,padx= 5,sticky = 'w')

                popup_label_address_relative = ctk.CTkLabel(popup_register_relation,text='ที่อยู่ : ',font=('TH SarabunPSK',18,'bold'))
                popup_label_address_relative.grid(row = 6,column = 0,columnspan = 2,padx= 5,sticky = 'e')

                popup_entry_address_relative = ctk.CTkEntry(popup_register_relation,font=('TH SarabunPSK',18),textvariable=address_var)
                popup_entry_address_relative.grid(row = 6,column = 2,columnspan = 2,padx= 5,sticky = 'w')

                popup_label_tel_relative = ctk.CTkLabel(popup_register_relation,text='เบอร์โทร : ',font=('TH SarabunPSK',18,'bold'))
                popup_label_tel_relative.grid(row = 7,column = 0,columnspan = 2,padx= 5,sticky = 'e')

                popup_entry_tel_relative = ctk.CTkEntry(popup_register_relation,font=('TH SarabunPSK',18),textvariable=tel_var,validate='key',validatecommand = (self.vcmd,'%P'))
                popup_entry_tel_relative.grid(row = 7,column = 2,columnspan = 2,padx= 5,sticky = 'w')

                popup_label_relation_relative = ctk.CTkLabel(popup_register_relation,text='ความสัมพันธ์ : ',font=('TH SarabunPSK',18,'bold'))
                popup_label_relation_relative.grid(row = 8,column = 0,columnspan = 2,padx= 5,sticky = 'e')
                popup_combo_relation_relative = ctk.CTkOptionMenu(popup_register_relation,values=['','ปู่','ย่า','ตา','ยาย','ลุง','ป้า','พ่อ','แม่','น้า','พี่ชาย','พี่สาว','น้องสาว','ลูกสาว','ลูกชาย'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
                popup_combo_relation_relative.grid(row = 8,column = 2,columnspan = 2,padx= 5,sticky = 'w')

                popup_button_submit = ctk.CTkButton(popup_register_relation,
                                                    text='บันทึกข้อมูล',
                                                    width=100,
                                                    font=('TH SarabunPSK',18,'bold'),
                                                    command=lambda:save_regis_relative_to_db())
                popup_button_submit.grid(row = 9,column = 0,padx = 5,columnspan = 4)

            def check_relative_id():
                print('fn check_relative_id')
                result = self.db.get_data_for_ralative_id(popup_entry_id_relative.get().strip())
                print(result)
                if result != None:
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
            
            def save_regis_relative_to_db():
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

                result = self.db.get_data_relation(prisoner_id)
                check_data = (prisoner_id, int(national_id_number))

                # ตรวจสอบข้อมูลซ้ำ
                if check_data in result:
                    messagebox.showinfo('แจ้งข้อมูลซ้ำ', f'รหัสประจำตัวเลขที่ {national_id_number} มีการบันทึกข้อมูลแล้ว')
                    return

                # ตรวจสอบจำนวนญาติ
                if len(result) >= 10:
                    messagebox.showerror('ข้อมูลญาติ', 'ข้อมูลญาติเกิน 10 คน')
                    return

                # บันทึกข้อมูล
                result_add = self.db.add_data_ralative_to_relatives(prisoner_id, data, relation)
                if result_add:
                    success = self.db.add_data_relation_to_ralations(prisoner_id, data, relation)
                else:
                    messagebox.showerror('การบันทึกข้อมูล','ไม่สามารถบันทึกข้อมูลได้')
                    return
                if success:
                    continue_save = messagebox.askyesno(
                        'แจ้งเตือนการบันทึกข้อมูล',
                        f'บันทึกข้อมูล "{title}{first_name} {last_name}" สำเร็จ ต้องการเพิ่มญาติอีกหรือไม่'
                    )
                    if continue_save:
                        clear_popup_regis()
                    else:
                        popup_register_relation.destroy()
                else:
                    messagebox.showerror('ข้อผิดพลาด', 'เกิดข้อผิดพลาดในการบันทึกข้อมูล')

            def clear_popup_regis():
                popup_entry_id_relative.delete(0,ctk.END)
                popup_combo_title_relative.set('นาย')
                popup_entry_fname_relative.delete(0,ctk.END)
                popup_entry_lname_relative.delete(0,ctk.END)
                popup_entry_address_relative.delete(0,ctk.END)
                popup_entry_tel_relative.delete(0,ctk.END)
                popup_combo_relation_relative.set('')

        # แสดงข้อมูลญาติ
        def show_list_relative():
            def resize_tree_columns():
                print('resize')
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

##############################################################################################################################################################################
#   ค้นหาผู้ต้องขังทั้งหมด
##############################################################################################################################################################################
    def search_all_prisoner(self):

        # insert ข้อมูลให้อยู่ในตาราง treeview
        def show_prisoners(data):
            for row in tree.get_children():
                tree.delete(row)
            for row in data:
                tree.insert('','end',values=row)

        # ค้นหาข้อมูลจากตาราง แค่คนเดียว 
        def search_one_var_prisoners():
            keyword = search_all_var.get().lower()
            filtered = [row for row in all_data if keyword in row[2].lower()]
            print(filtered)
            show_prisoners(filtered)

        def resize_tree_columns():
            tree_container.update_idletasks()
            total_width = tree_container.winfo_width()
            for col, ratio in column_ratios.items():
                tree.column(col,width=int(total_width * ratio),anchor='w')

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
        style.configure('Treeview',font =('TH SarabunPSK',18),rowheight = 35)
        style.configure('Treeview.Heading',font = ('TH SarabunPSK',18,'bold'))

        tree = ttk.Treeview(tree_container,columns=('prisoner_id','sex','f_name','l_name','lawsuit','level','dan'),show='headings',height=10)
        tree.heading('prisoner_id',text='รหัสประจำตัว')
        tree.heading('sex',text='เพศ')
        tree.heading('f_name',text='ชื่อ')
        tree.heading('l_name',text='นามสกุล')
        tree.heading('lawsuit',text='คดี')
        tree.heading('level',text='ชั้น')
        tree.heading('dan',text='แดน')

        tree.column('prisoner_id')
        tree.column('sex')
        tree.column('f_name')
        tree.column('l_name')
        tree.column('lawsuit')
        tree.column('level')
        tree.column('dan')

        scrollbar = ttk.Scrollbar(tree_container,orient='vertical',command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.grid(row=0,column=0,sticky='nsew')
        scrollbar.grid(row=0,column=1,sticky='ns')

        all_data = []

        column_ratios = {
            'prisoner_id' : 0.14,
            'sex' : 0.08,
            'f_name' : 0.19,
            'l_name' : 0.19,
            'lawsuit' : 0.20,
            'level' : 0.12,
            'dan' : 0.08
        }

        all_data = self.db.get_data_all()
        show_prisoners(all_data)
        tree.bind('<Configure>',lambda e:resize_tree_columns())

##############################################################################################################################################################################
    # ลงทะเบียนลายนิ้วมือ
##############################################################################################################################################################################
    def register_fingerprint(self):
        self.zkfp2.Init()
        self.zkfp2.OpenDevice(0)

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

        regis_fp_entry = ctk.CTkEntry(popup_register_fingerprint,width=150,font=('TH SarabunPSK',18))
        regis_fp_entry.grid(row = 1,column = 0,sticky = 'e',padx = 5,pady = 10)

        regis_fp_search_bt = ctk.CTkButton(popup_register_fingerprint,
                                                text='ค้นหาข้อมูล',
                                                width=150,
                                                font=('TH SarabunPSK',18,'bold'),
                                                command=lambda:get_data_relative())
        regis_fp_search_bt.grid(row=1,column = 1,sticky = 'w',padx = 5,pady = 10)
        show_regis_data_search = ctk.CTkFrame(popup_register_fingerprint)
        label_fingerprint_state = ctk.CTkLabel(show_regis_data_search,font=('TH SarabunPSK',18,'bold'),text='')

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

            combo_title = ctk.CTkOptionMenu(show_regis_data_search,values=['นาย','นาง','นางสาว'],variable=show_regis_title,font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
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
                button_submit.pack_forget()
                button_cancel.pack_forget()
                progressbar.pack(padx=10,pady=10)
                progressbar.start()
                def run():
                    label_on_popup_fingerprint.configure(text = 'เครื่องสแกนพร้อม\nกรุณาวางนิ้วมือบนเครื่อง')
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
                        label_on_popup_fingerprint.configure(text = 'กำลังบันทึกข้อมูล\nกรุณารอสักครู่')
                        result = self.db.set_fingerprint(show_regis_id_var.get(), bytes(regTemp))

                    if result:
                        popup_fingerprint.after(0, lambda: (
                            on_success(),
                        ))
                on_success=lambda:(
                    label_on_popup_fingerprint.configure(text = 'บันทึกเสร็จสิ้น'),
                    popup_fingerprint.after(1000,lambda:popup_fingerprint.destroy()),
                    self.zkfp2.CloseDevice(),
                    get_data_relative()
                    )
                threading.Thread(target=run, daemon=True).start()
        def on_close():
            print('ปิดหน้าต่าง popup_register_fingerprint')
            popup_register_fingerprint.destroy()

        popup_register_fingerprint.protocol("WM_DELETE_WINDOW", on_close)
##############################################################################################################################################################################
    # รายการจองเยี่ยม
##############################################################################################################################################################################
    def reserve_to_visit(self):
        class ALERT(ctk.CTkToplevel):
            def __init__(self,parent,msg = None,text_color = None,button=True):
                super().__init__(parent)
                self.geometry('300x200+840+440')
                self.grab_set()
                self.attributes('-topmost',True)
                self.title('แจ้งเตือน')
                self.overrideredirect(True)
                frame_border = ctk.CTkFrame(self,corner_radius=5,fg_color='black')
                frame_border.pack(fill = 'both',expand=True,padx = 2,pady = 2)
                frame_inner = ctk.CTkFrame(frame_border,corner_radius=3,)
                frame_inner.pack(fill ='both',expand = True,padx = 3,pady=3)
                if text_color is None:
                    text_color = 'red'
                for line in msg:
                    ctk.CTkLabel(
                        frame_inner,
                        text=line,
                        text_color=text_color,
                        font=('TH SarabunPSK',28,'bold')
                    ).pack(pady = 10)
                if button:
                    ctk.CTkButton(frame_inner,text='รับทราบ',font=('TH SarabunPSK',28,'bold'),command=lambda:self.destroy()).pack(side = 'bottom',pady = 20)

        popup_reserve_to_visit = ctk.CTkToplevel(self) 
        popup_reserve_to_visit.title('จองเยี่ยม')
        popup_reserve_to_visit.geometry('1280x720+1+1')
        popup_reserve_to_visit.grab_set()
        popup_reserve_to_visit.focus()
        # popup_reserve_to_visit.attributes('-fullscreen',True)

        popup_reserve_to_visit.grid_columnconfigure((0,1),weight=1,uniform='popup_reserve')
        popup_reserve_to_visit.grid_rowconfigure(1,weight=0,uniform='popup_reserve')
        progressbar = ctk.CTkProgressBar(popup_reserve_to_visit,mode='indeterminate')
        label_content = ctk.CTkLabel(popup_reserve_to_visit,text='',font=('TH SarabunPSK', 52, 'bold'))
        date_label = ctk.CTkLabel(popup_reserve_to_visit,font=('TH SarabunPSK', 52, 'bold'))
        relative_label = ctk.CTkLabel(popup_reserve_to_visit,font=('TH SarabunPSK', 46, 'bold'))
        flag_status = False
        nationnal_id = None
        popup_reserve_to_visit.bind('<Escape>',lambda:on_close())
        days = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์","อาทิตย์"]
        months = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน",
                    "พฤษภาคม","มิถุนายน","กรกฎาคม", "สิงหาคม",
                    "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]

        current_time = t.localtime()
        day = days[current_time.tm_wday]
        month = months[current_time.tm_mon - 1]

        def config_label():
            # relative_label.grid_forget()
            # tree_container.grid_forget()
            progressbar.grid(row = 2,column = 0 ,columnspan = 2,pady = 20)
            progressbar.stop()
            label_content.grid(row = 3,column = 0,columnspan = 2 ,sticky = 'nsew',pady = 20)
            date_label.grid(row=0,column=0,columnspan=2,sticky='n', pady=10)
            label_content.configure(text = 'กรุณาวางนิ้วมือบนเครื่องสแกนเพื่อเริ่มการจองเยี่ยม',text_color = 'black')
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
                        self.after(3000,config_label)
                        return
                    
                    progressbar.stop()
                    flag_status = False
                    progressbar.grid_forget()
                    label_content.grid_forget()

                    allowed_dan_by_dan = {
                        "จันทร์" : [5], 
                        "อังคาร" : [6], 
                        "พุธ" : [1,2,3,4,7], 
                        "พฤหัสบดี" : [5,6], 
                        "ศุกร์" : [1,2,3,4,7]
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
            try:
                self.zkfp2.Init()
                self.zkfp2.OpenDevice(0)
                progressbar.start()
                flag_status = True
            except Exception as e:
                print(f'เกิดข้อผิดพลาด {e}')
            get_capture_fingerprint()

        def item_select(_):
            try:
                for i in tree.selection():
                    prisoner_data = tree.item(i)['values']
                open_next_screen(prisoner_data)
                return
            except Exception as e:
                print(f'เกิดข้อผิดพลาด item_select(_) : {e}')

        def on_close():
            try:
                self.zkfp2.CloseDevice()
                print('Close Device')
            except Exception as e:
                print(f'ปิดอุปกรณ์ลายนิ้วมือไม่สำเร็จ : {e}')
            popup_reserve_to_visit.destroy()
        
        def open_next_screen(data):

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
                tree_container.grid_forget()
                relative_label.grid_forget()
                next_screen.destroy()
                config_label()

            def select_round():
                for widget in frame_select_round.winfo_children():
                    widget.destroy()
                    
                frame_follower_visit.pack_forget()
                frame_select_round.pack(fill = 'both',expand = True)

                label = ctk.CTkLabel(frame_select_round,text='เลือกรอบเยี่ยม',font=('TH SarabunPSK',40,'bold'))
                label.pack(pady = 5)
                content = ctk.CTkLabel(frame_select_round,text=f'{data[1]} {data[2]}',font=('TH SarabunPSK',30))
                content.pack(pady = 5)

                # รอบเวลาเช้า
                ctk.CTkLabel(frame_select_round,text='รอบเช้า',font=('TH SarabunPSK',32,'bold')).pack(pady = 10)
                for text,value in [('รอบที่ 1 เวลา 09.30 - 09.45','09:30'),
                                ('รอบที่ 2 เวลา 10.00 - 10.15','10:00'),
                                ('รอบที่ 3 เวลา 10.30 - 10.45','10:30'),
                                ('รอบที่ 4 เวลา 11.00 - 11.15','11:00')]:
                    ctk.CTkRadioButton(frame_select_round,
                                    text=text,
                                    variable = round_visit_var,
                                    value = value,
                                    font=('TH SarabunPSK',32,'bold')
                                    ).pack(pady = 5)

                # รอบเวลาบ่าย
                ctk.CTkLabel(frame_select_round,text='รอบบ่าย',font=('TH SarabunPSK',32,'bold')).pack(pady = 10)
                for text,value in [('รอบที่ 5 เวลา 13.15 - 13.30','13:15'),
                                ('รอบที่ 6 เวลา 13.45 - 14.00','13:45'),
                                ('รอบที่ 7 เวลา 14.15 - 14.30','14:15')]:
                    ctk.CTkRadioButton(frame_select_round,
                                    text=text,
                                    variable = round_visit_var,
                                    value=value,
                                    font=('TH SarabunPSK',32,'bold')
                                    ).pack(pady = 5)

                submit = ctk.CTkButton(frame_select_round,
                                    text='เลือกผู้ติดตาม',
                                    command=lambda:select_follower() if round_visit_var.get() else ALERT(frame_select_round,msg=['\nกรุณาเลือกรอบเยี่ยม']),
                                    font=('TH SarabunPSK',24,'bold'),
                                    height=100
                                    )
                
                cancel = ctk.CTkButton(frame_select_round,
                                    text='ยกเลิก',
                                    command=lambda:next_screen_on_close(),
                                    font=('TH SarabunPSK',24,'bold'),
                                    height=40,
                                    fg_color='red'
                                    )
                cancel.pack(side = 'bottom',pady = 10)
                submit.pack(side = 'bottom',pady = 10)

            def select_follower():
                for widget in frame_follower_visit.winfo_children():
                    widget.destroy()
                frame_select_round.pack_forget()
                frame_confirm_visit.pack_forget()
                
                frame_follower_visit.pack(fill = 'both',expand = True)
                text_from_round = f'จองเยี่ยม\n{data[1]} {data[2]}\nเยี่ยมเวลา {round_visit_var.get()} น.'
                ctk.CTkLabel(frame_follower_visit,text=text_from_round,font=('TH SarabunPSK',28)).pack(pady = 10)
                # date time จากการเลือกรอบเยี่ยม
                round_time = round_visit_var.get()
                round_time_strtime = (datetime.strptime(round_time,"%H:%M")).strftime("%H:%M:%S")
                date_current = datetime.now().strftime("%d/%m/%Y")

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
                                    command=lambda:confirm_visit(round_time_strtime,date_current),
                                    font=('TH SarabunPSK',24,'bold'),
                                    height=100
                                    )
                
                cancel = ctk.CTkButton(frame_follower_visit,
                                    text='ย้อนกลับ',
                                    command=lambda:select_round(),
                                    font=('TH SarabunPSK',24,'bold'),
                                    height=40,
                                    fg_color='red'
                                    )
                cancel.pack(side = 'bottom',pady = 10)
                submit.pack(side = 'bottom',pady = 10)

            def confirm_visit(round_time_strtime,date_current):
                for widget in frame_confirm_visit.winfo_children():
                    widget.destroy()

                frame_follower_visit.pack_forget()
                frame_confirm_visit.pack(fill = 'both',expand = True)
                ctk.CTkLabel(frame_confirm_visit,text='กรุณาตรวจสอบข้อมูลให้ถูกต้อง',font=('TH SarabunPSK',24,'bold')).pack(pady = 20)
                select_fl_id = [rid for rid,var in follower_vars if var.get()]
                prepare_data = [date_current,round_time_strtime,prisoner_id,nationnal_id]

                ctk.CTkLabel(frame_confirm_visit,text=f'จองเยี่ยม\n{data[1]} {data[2]}\nโดย {relative_dict.get(nationnal_id)}\nผู้ติดตาม',font=('TH SarabunPSK',28)).pack(pady = 5)
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
                        insert_succress(prepare_data[1])
                        return
                elif len(prepare_data) == 7:
                    query = "INSERT INTO visits (date_visit,time_visit,prisoner_id,relative_id_1,relative_id_2,relative_id_3,relative_id_4) VALUES (?,?,?,?,?,?,?)"
                    result = self.db.add_visits(query,prepare_data)
                    if result:
                        insert_succress(prepare_data[1])
                        return
                elif len(prepare_data) == 6:
                    query = "INSERT INTO visits (date_visit,time_visit,prisoner_id,relative_id_1,relative_id_2,relative_id_3) VALUES (?,?,?,?,?,?)"
                    result = self.db.add_visits(query,prepare_data)
                    if result:
                        insert_succress(prepare_data[1])
                        return
                elif len(prepare_data) == 5:
                    query = "INSERT INTO visits (date_visit,time_visit,prisoner_id,relative_id_1,relative_id_2) VALUES (?,?,?,?,?)"
                    result = self.db.add_visits(query,prepare_data)
                    if result:
                        insert_succress(prepare_data[1])
                        return
                elif len(prepare_data) == 4:
                    query = "INSERT INTO visits (date_visit,time_visit,prisoner_id,relative_id_1) VALUES (?,?,?,?)"
                    result = self.db.add_visits(query,prepare_data)
                    if result:
                        insert_succress(prepare_data[1])
                        return
                
            def insert_succress(time_visit):
                alert = ALERT(next_screen,[f'จองเยี่ยมเรียบร้อย\nกรุณามาก่อนเวลา {time_visit} น.'],'black',button=False)
                alert.after(3000,lambda:next_screen_on_close())
            
            select_round()
            next_screen.protocol("WM_DELETE_WINDOW", next_screen_on_close)

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
                c = canvas.Canvas(temp_pdf,pagesize=A4)
                width,height = A4
                
                # ฟรอน และ ระยะห่าง
                c.setFont("Helvetica-Bold",10)
                c.drawCentredString(width/2,height-2*cm,'รายงานรายชื่อล่าสุด')
                c.setFont("Helvetica",10)

                # หัวตารางและความกว้าง
                columns = tree["columns"]
                col_widths = [ (width -4*cm) / len(columns)] * len(columns)
                headers = [tree.heading(col)["text"] for col in columns]

                # ตำแหน่งเริ่ม
                start_x = 2*cm
                start_y = height -4 * cm
                row_height = 1*cm

                # วาดหัวตาราง
                x = start_x
                y = start_y
                for i,header in enumerate(headers):
                    c.rect(x,y,col_widths[i],row_height,stroke=1,fill=0)
                    c.drawString(x+0.2*cm,y+0.3*cm,header)
                    x += col_widths[i]
                
                # วาดข้อมูล
                y += row_height
                for child_id in tree.get_children():
                    x = start_x
                    values = tree.item(child_id,"values")
                    for i,value in enumerate(values):
                        c.rect(x,y,col_widths[i],row_height,stroke=1,fill=0)
                        text = str(value)

                        # จัดชิดขวาถ้าเป็นตัวเลข
                        if text.isdigit():
                            text_width = c.stringWidth(text,"Helvetica",10)
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
            round_time = combo_round.get()
            round_date = datetime.now().strftime("%d/%m/%Y")
            # round_date = '06/05/2025'
            data = [round_date,round_time]
            result =  self.db.get_visits(data)
            for row in tree.get_children():
                tree.delete(row)
            for row in result:
                tree.insert('','end',values=row)
            tree_container.grid(row = 2 ,column = 0 ,columnspan = 3)
            tree.grid(row=0)
            button_print = ctk.CTkButton(self.popup_report_visits,text='พิมพ์',command=lambda:print_table())
            button_print.grid(row= 3,column = 0 ,columnspan = 3 ,pady = 20)


        self.popup_report_visits.grid_columnconfigure((0,1,2),weight=1,uniform='popup_report_visits')
        label_content = ctk.CTkLabel(self.popup_report_visits,text='รายงาน',font=('TH SarabunPSK',32,'bold'))
        label_content.grid(row = 0 , column = 0 , columnspan = 3 ,sticky = 'ns')

        label_select_round = ctk.CTkLabel(self.popup_report_visits,text='เลือกรอบเยี่ยม',font=('TH SarabunPSK',32,'bold'))
        label_select_round.grid(row = 1,column = 0,sticky = 'e')

        combo_round = ctk.CTkOptionMenu(self.popup_report_visits,values=['09:30:00','10:00:00','10:30:00','11:00:00','13:15:00','13:45:00','14:15:00'],font=('TH SarabunPSK',18),dropdown_font=('TH SarabunPSK',18))
        combo_round.grid(row= 1,column = 1, sticky = 'ew',padx = 40,pady = 20)

        button = ctk.CTkButton(self.popup_report_visits,text='ค้นหา',font=('TH SarabunPSK',18),command=lambda:get_visits())
        button.grid(row = 1,column = 2 ,sticky = 'w')

        tree_container = ctk.CTkFrame(self.popup_report_visits)
        tree_container.grid_columnconfigure(0,weight=1)
        tree_container.grid_rowconfigure(1,weight=1)

        # กำหนด style สำหรับ treeview 
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Treeview',font =('TH SarabunPSK',18),rowheight = 35)
        style.configure('Treeview.Heading',font = ('TH SarabunPSK',18,'bold'))
        
        tree  = ttk.Treeview(tree_container,columns=('time_stamp','date_visit','time_visit','prisoner_id','relation_id_1','relation_id_2','relation_id_3','relation_id_4','relation_id_5'),show='headings',height=10)
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
        elif page_name == 'ผู้ต้องขังทั้งหมด':
            print(page_name)
            self.show_all_prisoner_frame.pack(fill='both',expand = True)
            self.search_all_prisoner()
        elif page_name == 'จองเยี่ยม':
            self.reserve_to_visit()
        elif page_name == 'ลงทะเบียนลายนิ้วมือ':
            self.register_fingerprint()
        elif page_name == 'รายงาน':
            self.popup_report_visits.pack(fill='both',expand = True)
            self.report_visits()
   