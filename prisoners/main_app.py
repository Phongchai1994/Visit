import customtkinter as ctk
import tkinter as tk
from tkinter import ttk,messagebox
from manage.database import SQLiteDB
import emoji
from pyzkfp import ZKFP2
import fingerprint.manage_fingerprint as zkfp
import threading
import time as t
from datetime import datetime

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
                data = [national_id_number,title,first_name,last_name,address,tel]
                relation = popup_combo_relation_relative.get().strip()

                result = self.db.get_data_relation(prisoner_id)
                check_data = (prisoner_id,int(national_id_number))

                for index,item in enumerate(result):
                    if result[index] == check_data:
                        messagebox.showinfo('แจ้งข้อมูลซ้ำ',f'รหัสประจำตัวเลขที่ {national_id_number} มีการบันทึกข้อมูลแล้ว')
                        break
                    else:
                        if len(result) < 10:
                            if all(data):
                                result = self.db.add_data_ralative_to_relatives(prisoner_id,data,relation)
                                print(f'result add_data_ralative_to_relatives = {result}')
                                if result:
                                    print(f'result = {result}')
                                    continue_save = messagebox.askyesno('แจ้งเตือนการบันทึกข้อมูล',f'บันทึกข้อมูล "{popup_combo_title_relative.get().strip()}{popup_entry_fname_relative.get().strip()} {popup_entry_lname_relative.get().strip()}" สำเร็จ ต้องการเพิ่มญาติอีกหรือไม่')
                                    if continue_save:
                                        clear_popup_regis()
                                    else:
                                        popup_register_relation.destroy()
                                else:
                                    result = self.db.add_data_relation_to_ralations(prisoner_id,data,relation)
                                    print(f'result add_data_relation_to_ralations = {result}')
                                    continue_save = messagebox.askyesno('แจ้งเตือนการบันทึกข้อมูล',f'บันทึกข้อมูล "{popup_combo_title_relative.get().strip()}{popup_entry_fname_relative.get().strip()} {popup_entry_lname_relative.get().strip()}" สำเร็จ ต้องการเพิ่มญาติอีกหรือไม่')
                                    if continue_save:
                                        clear_popup_regis()
                                    else:
                                        popup_register_relation.destroy()
                            else:
                                messagebox.showerror('แจ้งเตือน','กรุณากรอกข้อมูลให้ครบทุกช่อง')
                        else:
                            messagebox.showerror('ข้อมูลญาติ','ข้อมูลญาติเกิน 10 คน')
                        break

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
            nonlocal prisoner_id_in_search_one
            nonlocal prisoner_name_in_search_one
            popup_show_list = ctk.CTkToplevel(self)
            popup_show_list.title('รายชื่อญาติ')
            popup_show_list.geometry('720x480+1+1')
            popup_show_list.grab_set()
            # prisoner_id_in_search_one = showdata_id_data.cget('text')
            # prisoner_name_in_search_one = f'{showdata_fname_data} {showdata_lname_data}'
            ctk.CTkLabel(popup_show_list,text=f'ข้อมูลญาติของ {prisoner_name_in_search_one}',font=('TH SarabunPSK',40,'bold')).grid(row = 0,column = 0,sticky = 'nsew')

            tree_container = ctk.CTkFrame(popup_show_list)
            tree_container.grid(row = 2,column=0,padx=20, pady=10, sticky="nsew")

            tree_container.grid_rowconfigure(1,weight=1)
            tree_container.grid_columnconfigure(0,weight=1)

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

            tree.column('relative_id')
            tree.column('title')
            tree.column('f_name')
            tree.column('l_name')
            tree.column('address')
            tree.column('tel')
            tree.column('relation')

            scrollbar = ttk.Scrollbar(tree_container,orient='vertical',command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            tree.grid(row=1,column=0,sticky='nsew')
            scrollbar.grid(row=1,column=1,sticky='ns')

            result = self.db.get_join_prisoners_and_relatives(prisoner_id_in_search_one)
            print(result)
            for row in result:
                tree.insert('','end',values=row)

##############################################################################################################################################################################
#   ค้นหาผู้ต้องขังทั้งหมด
##############################################################################################################################################################################
    def search_all_prisoner(self):
        self.show_all_prisoner_frame.grid_rowconfigure(2,weight=1)
        self.show_all_prisoner_frame.grid_columnconfigure(0,weight=1)

        search_all_var = tk.StringVar()
        
        prisoner_select = None
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

        def show_prisoner_select():
            print(tree.selection())
            for i in tree.selection():
                print(tree.item(i)['values'])

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

        all_data = self.db.get_data_all()
        show_prisoners(all_data)

##############################################################################################################################################################################
    # ลงทะเบียนลายนิ้วมือ
##############################################################################################################################################################################
    def register_fingerprint(self):
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
            global popup_fingerprint
            popup_fingerprint = ctk.CTkToplevel(popup_register_fingerprint)
            popup_fingerprint.transient(popup_register_fingerprint)
            popup_fingerprint.title('เก็บลายนิ้วมือ')
            popup_fingerprint.geometry('300x300+450+200')
            popup_fingerprint.grab_set()
            popup_fingerprint.focus_set()

            global label_on_popup_fingerprint

            label_on_popup_fingerprint = ctk.CTkLabel(popup_fingerprint,text='กรุณาวางนิ้วบนเครื่องสแกน',font=('TH SarabunPSK',32,'bold'))
            label_on_popup_fingerprint.pack(expand = True,fill = 'both')

            buttton_submit = ctk.CTkButton(popup_fingerprint,
                                   text='บันทึกลายนิ้วมือ',
                                   font=('TH SarabunPSK',18,'bold'),
                                   command=lambda:start_capture())
            buttton_submit.pack(side='left',pady = 5)
            buttton_submit = ctk.CTkButton(popup_fingerprint,
                                   text='ยกเลิก',
                                   font=('TH SarabunPSK',18,'bold'),
                                   command=lambda:popup_fingerprint.destroy())
            buttton_submit.pack(side='right',pady = 5)

        def start_capture():
            zkfp.capture_fingerprint(
                zkfp2=self.zkfp2,
                label=label_on_popup_fingerprint,
                popup=popup_fingerprint,
                db=self.db,
                regis_id=show_regis_id_var.get(),
                on_success=lambda:(
                    messagebox.showinfo('แจ้งบันทึกลายนิ้วมือ','บันทึกลายนิ้วมือเสร็จสิ้น'),
                    get_data_relative()
                    )
                )

##############################################################################################################################################################################
    # รายการจองเยี่ยม
##############################################################################################################################################################################
    def reserve_to_visit(self):
        popup_reserve_to_visit = ctk.CTkToplevel(self) 
        popup_reserve_to_visit.title('จองเยี่ยม')
        popup_reserve_to_visit.geometry('1280x720+1+1')
        popup_reserve_to_visit.grab_set()

        popup_reserve_to_visit.grid_columnconfigure((0,1),weight=1,uniform='popup_reserve')
        popup_reserve_to_visit.grid_rowconfigure(1,weight=0,uniform='popup_reserve')

        progressbar = ctk.CTkProgressBar(popup_reserve_to_visit,mode='indeterminate')
        progressbar.grid(row = 2,column = 0 ,columnspan = 2,pady = 20)
        progressbar.stop()

        date_label = ctk.CTkLabel(popup_reserve_to_visit,font=('TH SarabunPSK', 52, 'bold'))
        date_label.grid(row=0,column=0,columnspan=2,sticky='n', pady=10)

        def update_time_label():
            days = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์","อาทิตย์"]
            months = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน",
                       "พฤษภาคม","มิถุนายน","กรกฎาคม", "สิงหาคม",
                         "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]

            current_time = t.localtime()
            day = days[current_time.tm_wday]
            month = months[current_time.tm_mon - 1]
            text = f"วัน {day} ที่ {current_time.tm_mday} {month} {(current_time.tm_year)+543} เวลา {t.strftime('%H:%M:%S')}"
            date_label.configure(text=text)
            if popup_reserve_to_visit.winfo_exists():
                popup_reserve_to_visit.after(1000,update_time_label)


        def get_capture_fingerprint():
            nonlocal capture_current
            capture = self.zkfp2.AcquireFingerprint()
            nationnal_id = None
            if capture:
                print('สแกนสำเร็จ',type(capture_current))
                tmp, img = capture
                capture_current = tmp
                print(type(capture_current))
                progressbar.stop()
                progressbar.grid_forget()
                result = self.db.get_all_fingerprint()
                for index,row in enumerate(result):
                    if row[1]:
                        fingerprint_in_db = row[1]
                        res = self.zkfp2.DBMatch(tmp,fingerprint_in_db)
                        
                        if res > 80 :
                            nationnal_id = row[0]
                            break
                if nationnal_id:
                    prisoners_data = self.db.get_join_relatives_and_prisoners(nationnal_id)
                else:
                    messagebox.showerror('แจ้งเตือนไม่พบข้อมูล','ไม่พบลายนิ้วมือ กรุณาเตรียมบัตรประชาชนติดต่อเจ้าหน้าที่')
                    progressbar.grid(row = 2,column = 0 ,columnspan = 2,pady = 20)
                    get_relative()
                    return
                print(prisoners_data)
                tree.grid(row=1,column=0,columnspan=2,sticky='nsew')
                tree_container.grid(row = 1,column=0,columnspan = 2,padx=20, pady=10, sticky="nsew")
                scrollbar.grid(row=1,column=1,sticky='ns')
                for row in tree.get_children():
                    tree.delete(row)
                for index,row in enumerate(prisoners_data):
                    tree.insert('','end',values=row)

            else:
                if popup_reserve_to_visit.winfo_exists():
                    self.after(500,get_capture_fingerprint)

        def get_relative():
            try:
                init = self.zkfp2.Init()
                opendevice = self.zkfp2.OpenDevice(0)
                progressbar.start()
            except Exception as e:
                print(f'เกิดข้อผิดพลาด {e}')
            get_capture_fingerprint()

        def item_select(_):
            for i in tree.selection():
                prisoner_data = tree.item(i)['values']
            open_next_screen(prisoner_data)

        def on_close():
            try:
                self.zkfp2.CloseDevice()
                print('Close Device')
            except Exception as e:
                print(f'ปิดอุปกรณ์ลายนิ้วมือไม่สำเร็จ : {e}')
            popup_reserve_to_visit.destroy()

        capture_current = None
        update_time_label()
        tree_container = ctk.CTkFrame(popup_reserve_to_visit)

        tree_container.grid_rowconfigure(1,weight=1)
        tree_container.grid_columnconfigure(0,weight=1)
        get_relative()

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

        def open_next_screen(prisoner_data):
            next_screen = ctk.CTkToplevel(popup_reserve_to_visit)
            next_screen.geometry('400x700')
            next_screen.title('เลือกรอบเยี่ยม')
            next_screen.grab_set()

            def insert_recerve_to_db():
                round_time = round_visit_var.get()
                round_time_strtime = (datetime.strptime(round_time,"%H:%M")).strftime("%H:%M:%S")
                date_current = datetime.now().strftime("%d-%m-%Y")
                print(round_time_strtime)
                print(date_current)

            def next_screen_on_close():
                next_screen.destroy()

            label = ctk.CTkLabel(next_screen,text='เลือกรอบ',font=('TH SarabunPSK',32,'bold'))
            label.pack(pady = 5)
            content = ctk.CTkLabel(next_screen,text=f'{prisoner_data[1]} {prisoner_data[2]}',font=('TH SarabunPSK',30,'bold'))
            content.pack(pady = 5)

            round_visit_var = ctk.StringVar()
                    # รอบเวลาเช้า

            ctk.CTkLabel(next_screen,text='เช้า',font=('TH SarabunPSK',24,'bold')).pack(pady = 10)
            for text,value in [('รอบที่ 1 เวลา 09.30 - 09.45','09:30'),
                               ('รอบที่ 2 เวลา 10.00 - 10.15','10:00'),
                               ('รอบที่ 3 เวลา 10.30 - 10.45','10:30'),
                               ('รอบที่ 4 เวลา 11.00 - 11.15','11:00')]:
                ctk.CTkRadioButton(next_screen,
                                   text=text,
                                   variable = round_visit_var,
                                   value = value,
                                   font=('TH SarabunPSK',24,'bold')
                                   ).pack(pady = 5)


            ctk.CTkLabel(next_screen,text='บ่าย',font=('TH SarabunPSK',24,'bold')).pack(pady = 10)

            for text,value in [('รอบที่ 5 เวลา 13.15 - 13.30','13:15'),
                               ('รอบที่ 6 เวลา 13.45 - 14.00','13:45'),
                               ('รอบที่ 7 เวลา 14.15 - 14.30','14:15')]:
                ctk.CTkRadioButton(next_screen,
                                   text=text,
                                   variable = round_visit_var,
                                   value=value,
                                   font=('TH SarabunPSK',24,'bold')
                                   ).pack(pady = 5)

            submit = ctk.CTkButton(next_screen,
                                   text='ยืนยันการจองเยี่ยม',
                                   command=lambda:insert_recerve_to_db(),
                                   font=('TH SarabunPSK',24,'bold'),
                                   height=100
                                   )
            submit.pack(pady = 20)
            cancel = ctk.CTkButton(next_screen,
                                   text='ยกเลิก',
                                   command=lambda:next_screen_on_close(),
                                   font=('TH SarabunPSK',24,'bold'),
                                   height=40,
                                   fg_color='red'
                                   )
            cancel.pack(pady = 20)

            

    # รายงานการเยี่ยม
    def report_visits(self):
        # หัวข้อ
        ctk.CTkLabel(self.popup_report_visits,text='รายงานการเยี่ยม',font=('TH SarabunPSK',40,'bold')).grid(row = 0,column = 0,pady = 10,sticky = 'n')

    # function แสดงหน้าตามปุ่มกดจากหน้า Menu Frame
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
   