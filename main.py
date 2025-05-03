import customtkinter as ctk
from prisoners.main_app import MainFrame
from prisoners.menu_app import MenuFrame

ctk.set_appearance_mode('system')
ctk.set_default_color_theme('blue')


class App_Prisoners(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry('1366x768+1+1')
        self.title('เยี่ยมญาติ')
        
        self.grid_columnconfigure(1,weight=1)
        self.grid_rowconfigure(0,weight=1)

        self.main_frame = MainFrame(self)
        self.menu_frame = MenuFrame(self,self.main_frame)

        self.grid_columnconfigure(0,minsize=250)
        print('app_prisoners')

if __name__ == "__main__":
    app = App_Prisoners()
    app.mainloop()