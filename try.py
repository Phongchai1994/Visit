import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox,ttk

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
                                            # command=lambda:clear_popup_regis()
                                            )
        popup_button_submit.grid(row = 6,column = 0,padx = 5,columnspan = 2,sticky ='e' )
        popup_button_cancel.grid(row = 6,column = 2,padx = 5,columnspan = 2,sticky ='w' )

        def on_close():
            print('popup register ถูกปิด')
            popup_register_relation.destroy()

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
                        result = self.db.get_join_prisoners_and_relatives(prisoner_id)
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
        
        result = self.db.get_join_prisoners_and_relatives(prisoner_id)
        print(result)
        for row in result:
            tree_relative.insert('','end',values=row)

        popup_window_delete_relative = None
        tree_relative.bind('<Configure>',lambda e:resize_tree_columns())
        tree_relative.bind("<Button-3>",show_menu_delete_relation)
        popup_show_list.protocol("WM_DELETE_WINDOW", on_close)


    def delete_relative():
        print('delete_relative')
        pass

    def move_dan_and_adjust_level(prisoner_id):
        def get_data_on_data_one():
            result = self.db.get_data_one(prisoner_id)
            print(result)
            
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
        sex_data = ctk.CTkLabel(search_frame,text='',font=('TH SarabunPSK',18))
        fname_data = ctk.CTkLabel(search_frame,text='',font=('TH SarabunPSK',18))
        lname_data = ctk.CTkLabel(search_frame,text='',font=('TH SarabunPSK',18))
        lawsuit_data = ctk.CTkLabel(search_frame,text='',font=('TH SarabunPSK',18))
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
        filtered = [row for row in all_data if keyword in row[2].lower()]
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
            show_relative(prisoner_id, f_name, l_name)

        def move_dan():
            popup_window.destroy()
            move_dan_and_adjust_level(prisoner_id)

        def delete_rel():
            popup_window.destroy()
            delete_relative()

        # สร้างปุ่มใน popup
        ctk.CTkButton(popup_window, text="➕ เพิ่มญาติ",font =('TH SarabunPSK',18,'bold'), command=add_rel, width=160).pack(padx=10, pady=(10, 5))
        ctk.CTkButton(popup_window, text="👥 ดูรายชื่อญาติ",font =('TH SarabunPSK',18,'bold'), command=show_rel, width=160).pack(padx=10, pady=5)
        ctk.CTkButton(popup_window, text="➡️ ย้ายแดน",font =('TH SarabunPSK',18,'bold'), command=move_dan, width=160).pack(padx=10, pady=5)
        # ctk.CTkButton(popup_window, text="🗑️ ลบชื่อญาติ",font =('TH SarabunPSK',18,'bold'), command=delete_rel, width=160, fg_color="red").pack(padx=10, pady=(5, 10))

        # เมื่อคลิกข้างนอก popup ให้ปิด
        popup_window.bind("<FocusOut>", lambda e: popup_window.destroy())
        popup_window.focus_set()

    # ผูกกับคลิกขวา
    tree.bind("<Button-3>", show_ctk_popup)
    tree.bind('<Configure>',lambda e:resize_tree_columns())
    popup_window = None
    all_data = []
    load_data_on_db()
        