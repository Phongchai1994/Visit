import customtkinter as ctk
from manage.database import SQLiteDB
from datetime import datetime,timedelta
import time as t

from prisoners.main_app import ALERT, MORING_ROUNDS,AFTERNOON_ROUNDS,CALCULATE_NEXT_DAY

class RESERVE:
    def __init__(self, main_window, prisoner_data,national_id,to_day,to_month):
        self.main_window = main_window
        self.national_id = national_id
        self.follower_vars = []
        self.next_screen = ctk.CTkToplevel(self.main_window)
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
        print(f'today = {self.today}')
        self.today_month = to_month
        print(f'today_month = {self.today_month}')

        days = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์","อาทิตย์"]
        current_time = t.localtime()
        self.thai_day = days[current_time.tm_wday]

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
            alert = ALERT(self.next_screen,['กรุณาตรวจสอบข้อมูล\nผู้ต้องขังผิดวินัยไม่สามารถจองเยี่ยมได้'],button=False)
            alert.after(3000,lambda: (alert.destroy(),self.next_screen.destroy()))
            return False
        return True

    def check_visit(self):
        # นับครั้งการเยี่ยม return count_today,count_month
        check_visit = self.db.get_count_visit(self.id, self.today, self.today_month)

        if check_visit[0] > 0 :
            alert = ALERT(self.next_screen,['กรุณาตรวจสอบข้อมูล\nผู้ต้องขังเยี่ยมได้ไม่เกิน 1 ครั้ง ต่อวัน'],button=False)
            alert.after(3000,lambda: (alert.destroy(),self.next_screen.destroy()))
            return False
        if self.level == 'เยี่ยม' and check_visit[1] >= 8 :
            alert = ALERT(self.next_screen,[f'กรุณาตรวจสอบข้อมูล\nชั้น {self.level}\nเยี่ยมได้ไม่เกิน 8 ครั้ง ต่อเดือน'],button=False)
            alert.after(3000,lambda: (alert.destroy(),self.next_screen.destroy()))
            return False
        if self.level == 'ดีมาก' and check_visit[1] >= 6 :
            alert = ALERT(self.next_screen,[f'กรุณาตรวจสอบข้อมูล\nชั้น {self.level}\nเยี่ยมได้ไม่เกิน 6 ครั้ง ต่อเดือน'],button=False)
            alert.after(3000,lambda: (alert.destroy(),self.next_screen.destroy()))
            return False
        if self.level == 'ดี' and check_visit[1] >= 4 :
            alert = ALERT(self.next_screen,[f'กรุณาตรวจสอบข้อมูล\nชั้น {self.level}\nเยี่ยมได้ไม่เกิน 4 ครั้ง ต่อเดือน'],button=False)
            alert.after(3000,lambda: (alert.destroy(),self.next_screen.destroy()))
            return False
        if self.level == 'กลาง' and check_visit[1] >= 3 :
            alert = ALERT(self.next_screen,[f'กรุณาตรวจสอบข้อมูล\nชั้น {self.level}\nเยี่ยมได้ไม่เกิน 3 ครั้ง ต่อเดือน'],button=False)
            alert.after(3000,lambda: (alert.destroy(),self.next_screen.destroy()))
            return False
        if self.level == 'ระหว่างพิจารณาคดี' and check_visit[1] >= 3 :
            alert = ALERT(self.next_screen,[f'กรุณาตรวจสอบข้อมูล\nชั้น {self.level}\nเยี่ยมได้ไม่เกิน 3 ครั้ง ต่อเดือน'],button=False)
            alert.after(3000,lambda: (alert.destroy(),self.next_screen.destroy()))
            return False
        if self.level == 'ปรับปรุง' and check_visit[1] >= 2 :
            alert = ALERT(self.next_screen,[f'กรุณาตรวจสอบข้อมูล\nชั้น {self.level}\nเยี่ยมได้ไม่เกิน 2 ครั้ง ต่อเดือน'],button=False)
            alert.after(3000,lambda: (alert.destroy(),self.next_screen.destroy()))
            return False
        if self.level == 'ปรับปรุงมาก' and check_visit[1] >= 1 :
            alert = ALERT(self.next_screen,[f'กรุณาตรวจสอบข้อมูล\nชั้น {self.level}\nเยี่ยมได้ไม่เกิน 1 ครั้ง ต่อเดือน'],button=False)
            alert.after(3000,lambda: (alert.destroy(),self.next_screen.destroy()))
            return False
        return True
    
    # เลือกรอบเยี่ยม
    def select_round(self):

        # สร้างหน้าต่างใหม่
        
        self.next_screen.configure(fg_color='#f4f7fa')
        # กำหนดขนาดหน้าต่าง
        screen_width = self.next_screen.winfo_screenwidth()
        screen_height = self.next_screen.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 800) // 2
        self.next_screen.geometry(f'400x750+{x}+{y}')
        # กำหนดชื่อหน้าต่าง
        self.next_screen.title('เลือกรอบเยี่ยม (จองเยี่ยมปกติ)')
        self.next_screen.grab_set()
        self.next_screen.attributes('-topmost',True)
        self.next_screen.minsize(400,800)
        self.next_screen.maxsize(400,800)

        morning = MORING_ROUNDS()
        afternoon = AFTERNOON_ROUNDS()
        for widget in self.frame_select_round.winfo_children():
            widget.destroy()

        self.frame_follower_visit.pack_forget()
        self.frame_select_round.pack(fill='both', expand=True)

        label = ctk.CTkLabel(self.frame_select_round, text='เลือกรอบเยี่ยม (จองเยี่ยมวันนี้)', font=('TH SarabunPSK', 40, 'bold'),text_color="#FF0505")
        label.pack(pady=5)
        content = ctk.CTkLabel(self.frame_select_round, text=f'{self.name} {self.surname}', font=('TH SarabunPSK', 30))
        content.pack(pady=5)
        now = datetime.now().time()

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
                        font=('TH SarabunPSK', 32, 'bold')
                    ).pack(pady=5)

        elif self.thai_day == 'จันทร์' and str(self.dan) == '6':
            # 🔹 รอบเช้า (เวลาแสดง, เวลาเริ่มจริง, เวลาปิด)
            ctk.CTkLabel(self.frame_select_round, text='รอบเช้า', font=('TH SarabunPSK', 32, 'bold')).pack(pady=10)
            for text, start in morning.get_available_rounds(now):
                ctk.CTkRadioButton(
                    self.frame_select_round,
                    text=text,
                    variable=self.round_visit_var,
                    value=start,
                    font=('TH SarabunPSK', 32, 'bold')
                ).pack(pady=5)

            # 🔹 รอบบ่าย
            ctk.CTkLabel(self.frame_select_round, text='รอบบ่าย', font=('TH SarabunPSK', 32, 'bold')).pack(pady=10)
            for text, start in afternoon.get_available_rounds(now):
                ctk.CTkRadioButton(
                    self.frame_select_round,
                    text=text,
                    variable=self.round_visit_var,
                    value=start,
                    font=('TH SarabunPSK', 32, 'bold')
                ).pack(pady=5)                                                                                                          

        elif self.thai_day == 'อังคาร' and str(self.dan) == '5':
            # 🔹 รอบเช้า (เวลาแสดง, เวลาเริ่มจริง, เวลาปิด)
            ctk.CTkLabel(self.frame_select_round, text='รอบเช้า', font=('TH SarabunPSK', 32, 'bold')).pack(pady=10)
            for text, start in morning.get_available_rounds(now):
                ctk.CTkRadioButton(
                    self.frame_select_round,
                    text=text,
                    variable=self.round_visit_var,
                    value=start,
                    font=('TH SarabunPSK', 32, 'bold')
                ).pack(pady=5)
            
            # 🔹 รอบบ่าย
            ctk.CTkLabel(self.frame_select_round, text='รอบบ่าย', font=('TH SarabunPSK', 32, 'bold')).pack(pady=10)
            for text, start in afternoon.get_available_rounds(now):
                ctk.CTkRadioButton(
                    self.frame_select_round,
                    text=text,
                    variable=self.round_visit_var,
                    value=start,
                    font=('TH SarabunPSK', 32, 'bold')
                ).pack(pady=5) 

        elif self.thai_day == 'พุธ' and str(self.dan) == '1' and self.type != 'ผู้ต้องกักขัง':
            # 🔹 รอบเช้า (เวลาแสดง, เวลาเริ่มจริง, เวลาปิด)
            ctk.CTkLabel(self.frame_select_round, text='รอบเช้า', font=('TH SarabunPSK', 32, 'bold')).pack(pady=10)
            for text, start in morning.get_available_rounds(now):
                ctk.CTkRadioButton(
                    self.frame_select_round,
                    text=text,
                    variable=self.round_visit_var,
                    value=start,
                    font=('TH SarabunPSK', 32, 'bold')
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
                        font=('TH SarabunPSK', 32, 'bold')
                    ).pack(pady=5)

        elif self.thai_day == 'พุธ' and str(self.dan) in ['2','3','4','7'] and self.type != 'ผู้ต้องกักขัง':                    
            # 🔹 รอบบ่าย
            ctk.CTkLabel(self.frame_select_round, text='รอบบ่าย', font=('TH SarabunPSK', 32, 'bold')).pack(pady=10)
            for text, start in afternoon.get_available_rounds(now):
                ctk.CTkRadioButton(
                    self.frame_select_round,
                    text=text,
                    variable=self.round_visit_var,
                    value=start,
                    font=('TH SarabunPSK', 32, 'bold')
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
                        font=('TH SarabunPSK', 32, 'bold')
                    ).pack(pady=5)

        elif self.thai_day == 'พฤหัสบดี' and str(self.dan) == '5':
            # 🔹 รอบเช้า (เวลาแสดง, เวลาเริ่มจริง, เวลาปิด)
            ctk.CTkLabel(self.frame_select_round, text='รอบเช้า', font=('TH SarabunPSK', 32, 'bold')).pack(pady=10)
            for text, start in morning.get_available_rounds(now):
                ctk.CTkRadioButton(
                    self.frame_select_round,
                    text=text,
                    variable=self.round_visit_var,
                    value=start,
                    font=('TH SarabunPSK', 32, 'bold')
                ).pack(pady=5)
                
        elif self.thai_day == 'พฤหัสบดี' and str(self.dan) == '6':
            # 🔹 รอบบ่าย
            ctk.CTkLabel(self.frame_select_round, text='รอบบ่าย', font=('TH SarabunPSK', 32, 'bold')).pack(pady=10)
            for text, start in afternoon.get_available_rounds(now):
                ctk.CTkRadioButton(
                    self.frame_select_round,
                    text=text,
                    variable=self.round_visit_var,
                    value=start,
                    font=('TH SarabunPSK', 32, 'bold')
                ).pack(pady=5)
        elif self.thai_day == 'ศุกร์' and str(self.dan) == '1' and self.type != 'ผู้ต้องกักขัง':
            # 🔹 รอบเช้า (เวลาแสดง, เวลาเริ่มจริง, เวลาปิด)
            ctk.CTkLabel(self.frame_select_round, text='รอบเช้า', font=('TH SarabunPSK', 32, 'bold')).pack(pady=10)
            for text, start in morning.get_available_rounds(now):
                ctk.CTkRadioButton(
                    self.frame_select_round,
                    text=text,
                    variable=self.round_visit_var,
                    value=start,
                    font=('TH SarabunPSK', 32, 'bold')
                ).pack(pady=5)

        elif self.thai_day == 'ศุกร์' and str(self.dan) in ['2','3','4','7'] and self.type != 'ผู้ต้องกักขัง':                    
            # 🔹 รอบบ่าย
            ctk.CTkLabel(self.frame_select_round, text='รอบบ่าย', font=('TH SarabunPSK', 32, 'bold')).pack(pady=10)
            for text, start in afternoon.get_available_rounds(now):
                ctk.CTkRadioButton(
                    self.frame_select_round,
                    text=text,
                    variable=self.round_visit_var,
                    value=start,
                    font=('TH SarabunPSK', 32, 'bold')
                ).pack(pady=5)
        
        # 🔸 ปุ่ม
        submit = ctk.CTkButton(
            self.frame_select_round,
            text='เลือกผู้ติดตาม',
            command=lambda: self.select_follower() if self.round_visit_var.get() else ALERT(self.frame_select_round, msg=['\nกรุณาเลือกรอบเยี่ยม']),
            font=('TH SarabunPSK', 24, 'bold'),
            height=100
        )

        cancel = ctk.CTkButton(
            self.frame_select_round,
            text='ยกเลิก',
            command=lambda:(self.on_close()),
            font=('TH SarabunPSK', 24, 'bold'),
            height=40,
            fg_color='red'
        )

        cancel.pack(side='bottom', pady=10)
        submit.pack(side='bottom', pady=10)

    def select_follower(self):
        reserve_date = datetime.now().strftime("%Y-%m-%d")
        for widget in self.frame_follower_visit.winfo_children():
            widget.destroy()
        self.frame_select_round.pack_forget()
        self.frame_confirm_visit.pack_forget()

        # date time จากการเลือกรอบเยี่ยม
        round_time = self.round_visit_var.get()
        round_time_strtime = (datetime.strptime(round_time,"%H:%M:%S")).strftime("%H:%M:%S")
        count_visit = self.db.get_count_visit_on_round(round_time,reserve_date)
        channel = int(count_visit) + 1
        
        print(f'count_visit = {count_visit}')

        if count_visit > 14:
            count_alert = ALERT(self.next_screen,['รอบเต็ม\nกรุณาเลือกรอบใหม่'],text_color='red',button=True)
            self.select_round()
            return

        self.frame_follower_visit.pack(fill = 'both',expand = True)
        text_from_round = f'จองเยี่ยม\n{self.name} {self.surname}\nเยี่ยมเวลา {self.round_visit_var.get()} น.'
        ctk.CTkLabel(self.frame_follower_visit,text=text_from_round,font=('TH SarabunPSK',28)).pack(pady = 10)


        followers = self.db.get_join_prisoners_and_relatives_not_follower(self.id,self.national_id)
        print(f'prisoner_id = {self.id}')
        print(f'nationnal_id = {self.national_id}')
        print(f'followers = {followers}')
        ctk.CTkLabel(self.frame_follower_visit,text='กรุณาเลือกผู้ติดตาม',font=('TH SarabunPSK',32,'bold')).pack(pady = 10)
        ctk.CTkLabel(self.frame_follower_visit,text='(เลือกผู้ติดตามได้สูงสุด 4 คน)',text_color='red',font=('TH SarabunPSK',24,'bold')).pack(pady = 10)
        if followers:
            for follower in followers:
                rid,title,fname,lname = follower
                if str(rid) == self.national_id:
                    break
                var = ctk.BooleanVar()
                chk = ctk.CTkCheckBox(self.frame_follower_visit,
                                    text=f'{title}{fname} {lname}',
                                    variable=var,
                                    font=('TH SarabunPSK',28,'bold'))
                chk.pack(pady = 5,padx = 50,anchor = 'nw')
                self.follower_vars.append((rid,var))
        else:
            ctk.CTkLabel(self.frame_follower_visit,text='ไม่มีผู้ติดตาม',font=('TH SarabunPSK',28,'bold')).pack(pady = 10)

        submit = ctk.CTkButton(self.frame_follower_visit,
                            text='ถัดไป',
                            command=lambda:self.confirm_visit(round_time_strtime,reserve_date,channel),
                            font=('TH SarabunPSK',24,'bold'),
                            height=100
                            )

        cancel = ctk.CTkButton(self.frame_follower_visit,
                            text='ย้อนกลับ',
                            command=lambda:self.select_round(),
                            font=('TH SarabunPSK',24,'bold'),
                            height=40,
                            fg_color='orange'
                            )
        cancel.pack(side = 'bottom',pady = 10)
        submit.pack(side = 'bottom',pady = 10)
    # ยืนยันข้อมูล
    def confirm_visit(self,round_time_strtime,reserve_date,channel):
        for widget in self.frame_confirm_visit.winfo_children():
            widget.destroy()

        self.frame_follower_visit.pack_forget()
        self.frame_confirm_visit.pack(fill = 'both',expand = True)
        ctk.CTkLabel(self.frame_confirm_visit,text='กรุณาตรวจสอบข้อมูลให้ถูกต้อง',font=('TH SarabunPSK',24,'bold')).pack(pady = 20)
        select_fl_id = [rid for rid,var in self.follower_vars if var.get()]
        prepare_data = [reserve_date,round_time_strtime,self.id,self.national_id]

        ctk.CTkLabel(self.frame_confirm_visit,text=f'จองเยี่ยม\n{self.name} {self.surname}\nเวลา {self.round_visit_var.get()} น.\nช่องเยี่ยมที่{channel}\nโดย {self.relative_dict.get(int(self.national_id))}\nผู้ติดตาม',font=('TH SarabunPSK',28)).pack(pady = 5)
        for index,row in enumerate(select_fl_id):
            prepare_data.append(row)
            ctk.CTkLabel(self.frame_confirm_visit,text=f'คนที่ {index +1} {self.relative_dict.get(row)}',font=('TH SarabunPSK',28)).pack(pady = 5)

        select_fl_id.clear()

        if len(prepare_data) > 8:
            print(f'ใน if = {prepare_data}')
            prepare_data.clear()
            self.follower_vars.clear()
            self.select_follower()
            alert = ALERT(self.frame_follower_visit,msg=['เลือกผู้ติดตามได้ไม่เกิน 4 คน','กรุณาเลือกใหม่'])
        
        submit = ctk.CTkButton(self.frame_confirm_visit,
                            text='ยืนยันการจองเยี่ยม',
                            command=lambda:self.insert_reserve_visit_to_db(prepare_data,channel),
                            font=('TH SarabunPSK',24,'bold'),
                            height=100
                            )

        back = ctk.CTkButton(self.frame_confirm_visit,
                            text='ย้อนกลับ',
                            command=lambda:go_back(),
                            font=('TH SarabunPSK',24,'bold'),
                            height=40,
                            fg_color='orange'
                            )
        cancel = ctk.CTkButton(self.frame_confirm_visit,
                            text='ยกเลิกการจอง',
                            command=lambda:(self.on_close()),
                            font=('TH SarabunPSK',24,'bold'),
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
    def insert_succress(self):
        alert = ALERT(self.next_screen,['จองเยี่ยมสำเร็จ'],button=True)
        result =alert.show()
        if result:
            self.on_close()

# mainwindows = ctk.CTk()
# mainwindows.geometry("800x600")
# mainwindows.title("Main Window")
# # reserve_now = RESERVE_NOW([1111111111, 'ทดสอบ', 'ทดสอบ', 'ระหว่างพิจารณาคดี', 1, 'พ่อ', 'อยู่', 'ผู้ต้องขัง'])

# if __name__ == "__main__":
#     # Example usage
#     prisoner_data = [1111111111, 'ทดสอบ', 'ทดสอบ', 'ระหว่างพิจารณาคดี', 1, 'พ่อ', 'อยู่', 'ผู้ต้องขัง']
#     national_id = '1560100345135'  # Example national ID
    
#     cal_next_day = CALCULATE_NEXT_DAY()

#     today_now = datetime.today().date().isoformat()
# #     month_now = today_now[:7]
#     cal_next_day = CALCULATE_NEXT_DAY()

#     today_future = cal_next_day.get_next_day()
#     month_future = today_future[:7]

#     month_now = today_now[:7]
#     month_future = today_future[:7]

#     print(type(today_now),f'today_now = {today_now}')
#     print(type(today_future),f'today_future = {today_future}')

#     print(type(month_now),f'month_now = {month_now}')
#     print(type(month_future),f'month_future = {month_future}')

#     reserve = RESERVE(mainwindows,prisoner_data,national_id,today_future,month_future)

#     mainwindows.mainloop()