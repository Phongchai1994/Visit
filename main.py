import customtkinter as ctk
from prisoners.main_app import MainFrame
from prisoners.menu_app import MenuFrame
import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import sys
import datetime
from manage.database import SQLiteDB
import hashlib

# ✅ เพิ่ม import user_session
from user_session import user_session, require_admin, require_login

ctk.set_appearance_mode('system')
ctk.set_default_color_theme('blue')

def resource_path(relative_path):
    """ให้ path ทำงานได้ทั้งตอนรันจาก .py และ .exe"""
    try:
        base_path = sys._MEIPASS  # pyinstaller สร้าง temp folder
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_config_path():
    return os.path.join(os.getcwd(), "config", "config.json")

def load_config():
    config_path = get_config_path()
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f).get('db_path')
    return ''

def save_config(file_path):
    config_path = get_config_path()
    os.makedirs(os.path.dirname(config_path), exist_ok=True)  # ✅ สร้างโฟลเดอร์ถ้ายังไม่มี
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump({'db_path': file_path}, f)

class App_Prisoners(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ✅ โหลด path ฐานข้อมูลจาก config
        self.db_path = load_config()
        
        # ✅ แสดงข้อมูลผู้ใช้ในหัวข้อ
        if user_session.is_logged_in:
            title = f'โปรแกรมจองเยี่ยมญาติ - {user_session.username} ({user_session.user_type.upper()})'
        else:
            title = 'โปรแกรมจองเยี่ยมญาติ'
        self.title(title)
        
        self.configure(fg_color='#ffffff')  # เปลี่ยนจาก '#f4f7fa' เป็น '#ffffff' เหมือน sidebar
        self.state('zoomed')  # เปิดหน้าต่างแบบ maximize
        self.update()

        # Modern shadowed sidebar
        sidebar = ctk.CTkFrame(self, fg_color='#ffffff', corner_radius=0, border_width=0)
        sidebar.grid(row=0, column=0, sticky='nsew')
        sidebar.grid_propagate(False)
        sidebar.configure(width=350)  # เพิ่มความกว้างจาก 270 เป็น 350
        sidebar.grid_rowconfigure(0, weight=1)  # ให้ sidebar สูงเต็มจอ
        sidebar.grid_columnconfigure(0, weight=1)  # ให้เนื้อหาใน sidebar กว้างเต็ม

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, minsize=350)  # เพิ่ม minsize จาก 270 เป็น 350

        # Main content area
        self.main_frame = MainFrame(self)
        self.menu_frame = MenuFrame(sidebar, self.main_frame)

        # ✅ เพิ่ม Status Bar
        self.create_status_bar()

        # Modern menubar (still native, but styled)
        menu_bar = tk.Menu(self, bg='#e3eefa', fg='#2d3a4b', activebackground='#b3d1ff', activeforeground='#2d3a4b')
        file_menu = tk.Menu(menu_bar, tearoff=0, bg='#f8fbff', fg='#2d3a4b')
        file_menu.add_command(label='เลือกฐานข้อมูล', command=self.select_database)
        file_menu.add_separator()
        
        # ✅ เพิ่มเมนูออกจากระบบ
        file_menu.add_command(label='ออกจากระบบ', command=self.logout)
        file_menu.add_separator()
        file_menu.add_command(label='รีเฟรชข้อมูล\tF5', command=self.refresh_all_data)
        file_menu.add_command(label='ปิดโปรแกรม', command=self.quit)
        menu_bar.add_cascade(label='ไฟล์', menu=file_menu)
        
        # ✅ เพิ่มเมนูสำหรับ Admin เท่านั้น
        if user_session.is_admin():
            admin_menu = tk.Menu(menu_bar, tearoff=0, bg='#f8fbff', fg='#2d3a4b')
            admin_menu.add_command(label='จัดการผู้ใช้', command=self.manage_users)
            admin_menu.add_command(label='รายงานระบบ', command=self.system_reports)
            admin_menu.add_command(label='ตั้งค่าระบบ', command=self.system_settings)
            admin_menu.add_separator()
            admin_menu.add_command(label='รีเฟรชระบบ', command=self.refresh_all_data)
            menu_bar.add_cascade(label='ผู้ดูแลระบบ', menu=admin_menu)
        
        # ✅ เพิ่มเมนูเครื่องมือ
        tools_menu = tk.Menu(menu_bar, tearoff=0, bg='#f8fbff', fg='#2d3a4b')
        tools_menu.add_command(label='รีเฟรชข้อมูล\tF5', command=self.refresh_all_data)
        tools_menu.add_command(label='ตรวจสอบการเชื่อมต่อ', command=self.check_database_connection)
        menu_bar.add_cascade(label='เครื่องมือ', menu=tools_menu)
        
        help_menu = tk.Menu(menu_bar, tearoff=0, bg='#f8fbff', fg='#2d3a4b')
        help_menu.add_command(label='เกี่ยวกับ')
        menu_bar.add_cascade(label='ช่วยเหลือ', menu=help_menu)
        self.config(menu=menu_bar)
        
        # ✅ เพิ่ม Keyboard Shortcuts
        self.bind('<F5>', lambda e: self.refresh_all_data())
        self.bind('<Control-r>', lambda e: self.refresh_all_data())
        self.bind('<Control-R>', lambda e: self.refresh_all_data())

    def create_status_bar(self):
        """สร้าง Status Bar แสดงข้อมูลผู้ใช้และฐานข้อมูล"""
        try:
            # ลบ status bar เดิมถ้ามี
            for widget in self.winfo_children():
                if isinstance(widget, ctk.CTkFrame) and widget.winfo_reqheight() == 30:
                    widget.destroy()
            
            # Status bar container สไตล์เหมือน sidebar
            status_frame = ctk.CTkFrame(
                self, 
                height=40,  # เพิ่มขนาดจาก 30 เป็น 40
                corner_radius=0,
                fg_color="#f4f7fa",  # สีเหมือน main.py
                border_width=1,
                border_color="#e0e6ed"
            )
            status_frame.grid(row=1, column=0, columnspan=2, sticky='ew')
            status_frame.grid_propagate(False)
            
            # Container สำหรับ status items
            status_container = ctk.CTkFrame(
                status_frame,
                fg_color="transparent"
            )
            status_container.pack(fill="both", expand=True, padx=10, pady=5)
            
            # ข้อมูลผู้ใช้
            if user_session.is_logged_in:
                user_info = f"ผู้ใช้: {user_session.username} | สิทธิ์: {user_session.user_type.upper()}"
                if user_session.login_time:
                    login_time_str = user_session.login_time.strftime("%d/%m/%Y %H:%M")
                    user_info += f" | เข้าสู่ระบบ: {login_time_str}"
            else:
                user_info = "ไม่ได้เข้าสู่ระบบ"
            
            # ✅ เพิ่มข้อมูลฐานข้อมูล (แสดงทั้ง Path)
            if hasattr(self, 'db_path') and self.db_path:
                user_info += f" | ฐานข้อมูล: {self.db_path}"
            else:
                user_info += " | ฐานข้อมูล: ไม่ได้เลือก"
            
            status_label = ctk.CTkLabel(
                status_container,
                text=user_info,
                font=("TH SarabunPSK", 14, "normal"),  # เปลี่ยนฟ้อนท์เป็น TH SarabunPSK
                text_color="#2d3a4b"  # สีเข้มสไตล์โมเดิล
            )
            status_label.pack(side='left', padx=5, pady=2)
            
            # # ✅ เพิ่มปุ่ม Refresh ใน Status Bar
            # refresh_btn = ctk.CTkButton(
            #     status_container,
            #     text="🔄 รีเฟรช",
            #     width=90,
            #     height=25,
            #     font=("TH SarabunPSK", 12, "bold"),
            #     fg_color="#4f8cff",
            #     hover_color="#3d7bd6",
            #     command=self.refresh_all_data
            # )
            # refresh_btn.pack(side='right', padx=5, pady=2)
            
            # # ✅ เพิ่มปุ่มตรวจสอบฐานข้อมูล
            # check_db_btn = ctk.CTkButton(
            #     status_container,
            #     text="📊 ตรวจสอบ DB",
            #     width=110,
            #     height=25,
            #     font=("TH SarabunPSK", 12, "bold"),
            #     fg_color="#26a69a",
            #     hover_color="#1e8e85",
            #     command=self.check_database_connection
            # )
            # check_db_btn.pack(side='right', padx=5, pady=2)
            
            
        except Exception as e:
            print(f"Error creating status bar: {e}")

    def select_database(self):
        # # ✅ ตรวจสอบสิทธิ์ก่อนให้เลือกฐานข้อมูล
        # if not user_session.is_admin():
        #     messagebox.showerror("ไม่มีสิทธิ์", "เฉพาะผู้ดูแลระบบเท่านั้นที่สามารถเลือกฐานข้อมูลได้")
        #     return
            
        file_path = filedialog.askopenfilename(
            title="เลือกไฟล์ฐานข้อมูล",
            filetypes=[('SQLite Database', '*.db'), ('All Files', '*.*')]
        )
        
        if file_path:
            # ✅ อัปเดต path ฐานข้อมูลใหม่
            self.db_path = file_path
            save_config(file_path)
            
            # ✅ Force reload database path ใน modules
            import importlib
            import manage.database
            importlib.reload(manage.database)
            
            # ✅ อัปเดตข้อมูลใน main_frame และ menu_frame
            self.refresh_database_connection()
            
            # ✅ รีเฟรชข้อมูลทั้งหมด
            self.refresh_all_data()
            
            messagebox.showinfo("สำเร็จ", 
                f"เปลี่ยนฐานข้อมูลเรียบร้อยแล้ว\n"
                f"ไฟล์: {os.path.basename(file_path)}\n"
                f"Path: {file_path}")

    def refresh_all_data(self):
        """รีเฟรชข้อมูลทั้งหมดในโปรแกรม"""
        try:
            print("เริ่มรีเฟรชข้อมูลทั้งหมด...")
            
            # ✅ รีเฟรชข้อมูลใน main_frame
            try:
                if hasattr(self.main_frame, 'refresh_data'):
                    self.main_frame.refresh_data()
                    print("รีเฟรช MainFrame สำเร็จ")
                else:
                    print("MainFrame ไม่มี method refresh_data")
            except Exception as e:
                print(f"Error refreshing MainFrame: {e}")
            
            # ✅ รีเฟรชข้อมูลใน menu_frame
            try:
                if hasattr(self.menu_frame, 'refresh_data'):
                    self.menu_frame.refresh_data()
                    print("รีเฟรช MenuFrame สำเร็จ")
                else:
                    print("MenuFrame ไม่มี method refresh_data")
            except Exception as e:
                print(f"Error refreshing MenuFrame: {e}")
            
            # ✅ อัปเดต status bar
            try:
                self.update_status_bar()
                print("อัปเดต Status Bar สำเร็จ")
            except Exception as e:
                print(f"Error updating status bar: {e}")
            
            # ✅ อัปเดตหัวข้อ
            try:
                self.update_title()
                print("อัปเดตหัวข้อสำเร็จ")
            except Exception as e:
                print(f"Error updating title: {e}")
            
            # ✅ แสดงข้อความยืนยัน
            db_name = os.path.basename(self.db_path) if self.db_path else 'ไม่ได้เลือก'
            current_time = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            
            messagebox.showinfo("สำเร็จ", 
                f"รีเฟรชข้อมูลทั้งหมดเรียบร้อยแล้ว\n"
                f"ฐานข้อมูล: {db_name}\n"
                f"เวลา: {current_time}")
            
            print("รีเฟรชข้อมูลทั้งหมดเสร็จสิ้น")
            
        except Exception as e:
            error_msg = f"เกิดข้อผิดพลาดในการรีเฟรช: {str(e)}"
            print(error_msg)
            messagebox.showerror("ข้อผิดพลาด", error_msg)

    def update_title(self):
        """อัปเดตหัวข้อของโปรแกรม"""
        if user_session.is_logged_in:
            title = f'โปรแกรมจองเยี่ยมญาติ - {user_session.username} ({user_session.user_type.upper()})'
        else:
            title = 'โปรแกรมจองเยี่ยมญาติ'
        
        if self.db_path:
            db_name = os.path.basename(self.db_path)
            title += f' - {db_name}'
        
        self.title(title)

    def refresh_database_connection(self):
        """รีเฟรชการเชื่อมต่อฐานข้อมูลใหม่"""
        try:
            print(f"กำลังอัปเดตการเชื่อมต่อฐานข้อมูล: {self.db_path}")
            
            # ✅ Force reload config ให้แน่ใจว่าได้ path ใหม่
            from manage.database import load_config
            current_path = load_config()
            print(f"Current config path: {current_path}")
            print(f"New path: {self.db_path}")
            
            # ✅ อัปเดต path ให้กับ main_frame
            try:
                if hasattr(self.main_frame, 'update_database_path'):
                    self.main_frame.update_database_path(self.db_path)
                    print("อัปเดต path ใน MainFrame สำเร็จ")
                else:
                    print("MainFrame ไม่มี method update_database_path")
            except Exception as e:
                print(f"Error updating MainFrame database path: {e}")
            
            # ✅ อัปเดต path ให้กับ menu_frame
            try:
                if hasattr(self.menu_frame, 'update_database_path'):
                    self.menu_frame.update_database_path(self.db_path)
                    print("อัปเดต path ใน MenuFrame สำเร็จ")
                else:
                    print("MenuFrame ไม่มี method update_database_path")
            except Exception as e:
                print(f"Error updating MenuFrame database path: {e}")
            
            # ✅ รีเฟรชข้อมูลที่แสดงอยู่
            try:
                if hasattr(self.main_frame, 'refresh_data'):
                    self.main_frame.refresh_data()
                    print("รีเฟรชข้อมูลใน MainFrame สำเร็จ")
            except Exception as e:
                print(f"Error refreshing MainFrame data: {e}")
            
            # ✅ อัปเดต status bar
            try:
                self.update_status_bar()
                print("อัปเดต Status Bar สำเร็จ")
            except Exception as e:
                print(f"Error updating status bar: {e}")
            
            print(f"Database path updated to: {self.db_path}")
            
        except Exception as e:
            error_msg = f"เกิดข้อผิดพลาดในการอัปเดตฐานข้อมูล: {str(e)}"
            print(error_msg)
            messagebox.showerror("ข้อผิดพลาด", error_msg)

    def update_status_bar(self):
        """อัปเดต Status Bar พร้อมข้อมูลฐานข้อมูล"""
        try:
            # ลบ status bar เดิม
            for widget in self.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    # ตรวจสอบว่าเป็น status bar หรือไม่
                    if widget.winfo_reqheight() == 40:
                        widget.destroy()
                        break
            
            # สร้าง status bar ใหม่
            self.create_status_bar()
            
        except Exception as e:
            print(f"Error updating status bar: {e}")
            # หากเกิดข้อผิดพลาด ให้สร้าง status bar ใหม่เลย
            self.create_status_bar()

    def check_database_connection(self):
        """ตรวจสอบการเชื่อมต่อฐานข้อมูล"""
        try:
            if not self.db_path:
                messagebox.showwarning("คำเตือน", "ยังไม่ได้เลือกไฟล์ฐานข้อมูล")
                return
            
            if not os.path.exists(self.db_path):
                messagebox.showerror("ข้อผิดพลาด", f"ไม่พบไฟล์ฐานข้อมูล:\n{self.db_path}")
                return
            
            # ทดสอบการเชื่อมต่อ
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()
            
            table_list = [table[0] for table in tables]
            table_info = f"ตาราง: {', '.join(table_list)}" if table_list else "ไม่พบตาราง"
            
            messagebox.showinfo("การเชื่อมต่อฐานข้อมูล", 
                f"เชื่อมต่อสำเร็จ!\n"
                f"ไฟล์: {os.path.basename(self.db_path)}\n"
                f"ขนาด: {os.path.getsize(self.db_path)} bytes\n"
                f"{table_info}")
            
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการเชื่อมต่อ:\n{str(e)}")

    # ✅ เพิ่มฟังก์ชันสำหรับ Admin
    def manage_users(self):
        messagebox.showinfo("จัดการผู้ใช้", "ฟีเจอร์จัดการผู้ใช้ (เฉพาะ Admin)")
    
    def system_reports(self):
        messagebox.showinfo("รายงานระบบ", "ฟีเจอร์รายงานระบบ (เฉพาะ Admin)")
    
    def system_settings(self):
        messagebox.showinfo("ตั้งค่าระบบ", "ฟีเจอร์ตั้งค่าระบบ (เฉพาะ Admin)")
    
    def logout(self):
        """ออกจากระบบ"""
        if messagebox.askyesno("ยืนยัน", "คุณต้องการออกจากระบบหรือไม่?"):
            user_session.logout()
            self.destroy()
            # กลับไปหน้า Login
            app = SimpleLoginApp()
            app.run()

class SimpleLoginApp:
    def __init__(self):
        # ตรวจสอบและบังคับเลือกฐานข้อมูลก่อนเข้าสู่ระบบ
        self.ensure_database_selected()

        # ...existing code...

    def ensure_database_selected(self):
        config_path = os.path.join(os.getcwd(), "config", "config.json")
        db_path = ''
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    db_path = json.load(f).get('db_path', '')
            except Exception:
                db_path = ''
        if not db_path or not os.path.exists(db_path):
            messagebox.showwarning("เลือกฐานข้อมูล", "กรุณาเลือกไฟล์ฐานข้อมูลก่อนเข้าสู่ระบบ")
            file_path = filedialog.askopenfilename(
                title="เลือกไฟล์ฐานข้อมูล",
                filetypes=[('SQLite Database', '*.db'), ('All Files', '*.*')]
            )
            if file_path:
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump({'db_path': file_path}, f)
            else:
                messagebox.showerror("ข้อผิดพลาด", "ต้องเลือกไฟล์ฐานข้อมูลก่อนใช้งาน")
                exit()

        # สร้างหน้าต่างหลัก
        self.root = ctk.CTk()
        self.root.title("ระบบเข้าสู่ระบบ - โปรแกรมจองเยี่ยมญาติ")
        self.root.geometry("450x500")  # ลดความสูงจาก 600 เป็น 500
        self.root.resizable(False, False)
        
        # Modern color scheme เหมือนกับ main.py
        self.root.configure(fg_color="#f4f7fa")
        
        # จัดกึ่งกลางหน้าจอ
        self.center_window()
        
        # สร้าง UI
        self.create_ui()
        
    def center_window(self):
        """จัดหน้าต่างให้อยู่กลางจอ"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.root.winfo_screenheight() // 2) - (500 // 2)  # ปรับจาก 600 เป็น 500
        self.root.geometry(f"450x500+{x}+{y}")
        
    def create_ui(self):
        """สร้าง UI ทั้งหมด - เฉพาะ content_frame"""
        # Login form card - สีขาวเหมือน sidebar ใน main.py
        form_frame = ctk.CTkFrame(
            self.root,
            fg_color="white",
            border_width=1,
            border_color="#e0e6ed",
            corner_radius=12
        )
        form_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Form content
        content_frame = ctk.CTkFrame(
            form_frame,
            fg_color="transparent"
        )
        content_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Welcome message
        welcome_label = ctk.CTkLabel(
            content_frame,
            text="ยินดีต้อนรับเข้าสู่ระบบ",
            font=("TH SarabunPSK", 24, "bold"),
            text_color="#2d3a4b"
        )
        welcome_label.pack(pady=(0, 20))
        
        # Username section
        username_label = ctk.CTkLabel(
            content_frame,
            text="ชื่อผู้ใช้",
            font=("TH SarabunPSK", 20, "bold"),
            text_color="#2d3a4b"
        )
        username_label.pack(anchor="w", pady=(10, 5))
        
        self.username_entry = ctk.CTkEntry(
            content_frame,
            placeholder_text="กรุณาใส่ชื่อผู้ใช้",
            height=45,
            font=("TH SarabunPSK", 20),
            border_color="#b3d1ff",
            border_width=2
        )
        self.username_entry.pack(fill="x", pady=(0, 15))
        
        # Password section
        password_label = ctk.CTkLabel(
            content_frame,
            text="รหัสผ่าน",
            font=("TH SarabunPSK", 20, "bold"),
            text_color="#2d3a4b"
        )
        password_label.pack(anchor="w", pady=(5, 5))
        
        self.password_entry = ctk.CTkEntry(
            content_frame,
            placeholder_text="กรุณาใส่รหัสผ่าน",
            height=45,
            font=("TH SarabunPSK", 20),
            border_color="#b3d1ff",
            border_width=2,
            show="*"
        )
        self.password_entry.pack(fill="x", pady=(0, 25))
        
        # Login button - สไตล์เหมือนปุ่มใน main.py
        login_btn = ctk.CTkButton(
            content_frame,
            text="🔑 เข้าสู่ระบบ",
            height=50,
            font=("TH SarabunPSK", 20, "bold"),
            fg_color="#4f8cff",
            hover_color="#3d7bd6",
            command=self.login
        )
        login_btn.pack(fill="x", pady=(0, 15))
        
        # Clear button
        clear_btn = ctk.CTkButton(
            content_frame,
            text="🗑️ ล้างข้อมูล",
            height=45,
            font=("TH SarabunPSK", 20, "bold"),
            fg_color="#ff6b6b",
            hover_color="#ff5252",
            command=self.clear_data
        )
        clear_btn.pack(fill="x", pady=(0, 15))

        
        # Event bindings
        self.root.bind('<Return>', lambda e: self.login())
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        
        # Focus ที่ username
        self.username_entry.focus()
        
    def login(self):
        """ฟังก์ชันเข้าสู่ระบบ"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username:
            messagebox.showerror("ข้อผิดพลาด", "กรุณากรอกชื่อผู้ใช้")
            self.username_entry.focus()
            return
            
        if not password:
            messagebox.showerror("ข้อผิดพลาด", "กรุณากรอกรหัสผ่าน")
            self.password_entry.focus()
            return
        
        # ✅ ระบบ Login ที่สมบูรณ์
        user_type = self.authenticate_user(username, password)
        
        if user_type:
            # บันทึกข้อมูล session
            user_session.login(username, user_type)
            
            # messagebox.showinfo("สำเร็จ", 
            #     f"เข้าสู่ระบบสำเร็จ!\n"
            #     f"ยินดีต้อนรับ {username}\n"
            #     f"สิทธิ์: {user_type.upper()}")
            
            self.open_main_app()
        else:
            messagebox.showerror("ข้อผิดพลาด", "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
            self.password_entry.delete(0, 'end')
            self.password_entry.focus()
    
    def authenticate_user(self, username, password):
        # print(f'ตรวจสอบผู้ใช้: {username}')
        # print(f'รหัสผ่านที่กรอก: {password}')
        """ตรวจสอบ username และ password"""
        # ✅ ข้อมูล Login (ในการใช้งานจริงควรเก็บในฐานข้อมูลและเข้ารหัส)
        users_db = SQLiteDB().get_users()
        print(f'ข้อมูลผู้ใช้ในฐานข้อมูล: {users_db}')
        if username in users_db:
            # password_hash = hashlib.sha256(password.encode('utf-8')).digest()

            # แปลง password ที่กรอกเป็น hash (BLOB)
            password_hash = hashlib.sha256(password.encode('utf-8')).digest()
            # print(f'รหัสผ่านที่แปลงเป็น hash: {password_hash}')
            if users_db[username]['password'] == password_hash:
                print(f'ประเภทผู้ใช้: {users_db[username]["user_type"]}')
                return users_db[username]['user_type']
        return None
    
    def clear_data(self):
        """ล้างข้อมูล"""
        self.username_entry.delete(0, 'end')
        self.password_entry.delete(0, 'end')
        self.username_entry.focus()
        
    def open_main_app(self):
        """เปิดหน้าหลัก"""
        self.root.destroy()
        
        main_app = App_Prisoners()
        main_app.mainloop()
        
    def run(self):
        """รันโปรแกรม"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SimpleLoginApp()
    app.run()
