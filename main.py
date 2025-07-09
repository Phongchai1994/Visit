import customtkinter as ctk
from prisoners.main_app import MainFrame
from prisoners.menu_app import MenuFrame
import tkinter as tk
from tkinter import filedialog
import json
import os
import sys

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
        # self.geometry('1366x768+1+1')
        self.title('โปรแกรมจองเยี่ยมญาติ')
        self.configure(fg_color='#f4f7fa')
        self.state('zoomed')  # เปิดหน้าต่างแบบ maximize
        self.update()

        # Modern shadowed sidebar
        sidebar = ctk.CTkFrame(self, fg_color='#ffffff', corner_radius=0, border_width=0)
        sidebar.grid(row=0, column=0, sticky='nswe')
        sidebar.grid_propagate(False)
        sidebar.configure(width=270)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, minsize=270)

        # Main content area
        self.main_frame = MainFrame(self)
        self.menu_frame = MenuFrame(sidebar, self.main_frame)

        # Modern menubar (still native, but styled)
        menu_bar = tk.Menu(self, bg='#e3eefa', fg='#2d3a4b', activebackground='#b3d1ff', activeforeground='#2d3a4b')
        file_menu = tk.Menu(menu_bar, tearoff=0, bg='#f8fbff', fg='#2d3a4b')
        file_menu.add_command(label='เลือกฐานข้อมูล', command=self.select_database)
        file_menu.add_separator()
        file_menu.add_command(label='ปิดโปรแกรม', command=self.quit)
        menu_bar.add_cascade(label='ไฟล์', menu=file_menu)
        help_menu = tk.Menu(menu_bar, tearoff=0, bg='#f8fbff', fg='#2d3a4b')
        help_menu.add_command(label='เกี่ยวกับ')
        menu_bar.add_cascade(label='ช่วยเหลือ', menu=help_menu)
        self.config(menu=menu_bar)

    def select_database(self):
        file_path = filedialog.askopenfilename(filetypes=[('SQLite Database', '*.db')])
        if file_path:
            self.db_path = file_path
            save_config(file_path)  # จะสร้าง config/config.json พร้อมโฟลเดอร์ถ้ายังไม่มี

if __name__ == "__main__":
    app = App_Prisoners()
    app.mainloop()