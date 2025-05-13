import customtkinter as ctk
from prisoners.main_app import MainFrame
from prisoners.menu_app import MenuFrame
import tkinter as tk
from tkinter import filedialog
import json
import os
import sys

def resource_path(relative_path):
    """ให้ path ทำงานได้ทั้งตอนรันจาก .py และ .exe"""
    try:
        base_path = sys._MEIPASS  # pyinstaller สร้าง temp folder
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

ctk.set_appearance_mode('system')
ctk.set_default_color_theme('blue')

def get_config_path():
    """ คืน path ที่เขียนได้ (ไม่ใช้ resource_path) """
    return os.path.join(os.getcwd(), "config\config.json")

def load_config():
    config_path = get_config_path()
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f).get('db_path')
    return ''

def save_config(file_path):
    config_path = get_config_path()
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump({'db_path': file_path}, f)

class App_Prisoners(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry('1366x768+1+1')
        self.title('โปรแกรมจองเยี่ยมญาติ')
        # self.attributes('-fullscreen',True)
        
        self.grid_columnconfigure(1,weight=1)
        self.grid_rowconfigure(0,weight=1)

        self.main_frame = MainFrame(self)
        self.menu_frame = MenuFrame(self,self.main_frame)

        self.grid_columnconfigure(0,minsize=250)

        # สร้างเมนูบาร์
        menu_bar = tk.Menu(self)
        # สร้างเมนู ไฟล์
        file_menu = tk.Menu(menu_bar,tearoff=0)
        file_menu.add_command(label='เลือกฐานข้อมูล',command=self.select_database)
        file_menu.add_separator()
        file_menu.add_command(label='ปิดโปรแกรม',command=self.quit)
        menu_bar.add_cascade(label='ไฟล์',menu=file_menu)
        # สร้างเมนู help
        help_menu = tk.Menu(menu_bar,tearoff=0)
        help_menu.add_command(label='เกี่ยวกับ')
        menu_bar.add_cascade(label='ช่วยเหลือ',menu = help_menu)
        self.config(menu=menu_bar)

    def select_database(self):
        file_path = filedialog.askopenfilename(filetypes=[('SQLite Database', '*.enc')])
        if file_path:
            self.db_path = file_path
            save_config(file_path)  # อัปเดต path ไปยัง config.json (เขียนได้)

if __name__ == "__main__":
    app = App_Prisoners()
    app.mainloop()