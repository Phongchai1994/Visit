import customtkinter as ctk
from prisoners.main_app import MainFrame
from prisoners.menu_app import MenuFrame
import tkinter as tk
from tkinter import filedialog
import json
import os

ctk.set_appearance_mode('system')
ctk.set_default_color_theme('blue')

CONFIG_FILE = os.path.join("config","config.json")

class App_Prisoners(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry('1366x768+1+1')
        self.title('โปรแกรมจองเยี่ยมญาติ')
        
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
        file_path = filedialog.askopenfilename(filetypes=[('SQLite Database','*.enc')])
        if file_path:
            self.db_path = file_path
            self.save_config(file_path)

    def save_config(self,file_path):
        # บันทึกค่าฐานข้อมูลที่เลือกลง config.json
        os.makedirs(os.path.dirname(CONFIG_FILE),exist_ok=True)
        with open(CONFIG_FILE,'w') as f:
            json.dump({'db_path':file_path},f)

if __name__ == "__main__":
    app = App_Prisoners()
    app.mainloop()