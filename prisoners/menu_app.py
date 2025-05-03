import customtkinter as ctk

class MenuFrame(ctk.CTkFrame):
    def __init__(self,parent,main_frame):
        super().__init__(parent,fg_color='#B6B6B6')
        
        self.grid(row=0,column=0,sticky='nsew')

        self.main_frame = main_frame # connect to main frame

        # create button
        ctk.CTkLabel(self,
                     text='เมนูจัดการข้อมูลผู้ต้องขัง',
                     font=('TH SarabunPSK',28,'bold')
                     ).pack(pady=10)
        ctk.CTkButton(self,
                      text='ลงทะเบียนผู้ต้องขัง',
                      border_color='black',
                      border_width=2,
                      font=('TH SarabunPSK',20,'bold'),
                      text_color='black',
                      fg_color='#87BFE5',
                      command=lambda:self.main_frame.show_page('ลงทะเบียนผู้ต้องขัง')
                      ).pack(pady=10)
        ctk.CTkButton(self,
                      text='ค้นหาผู้ต้องขัง',
                      border_color='black',
                      border_width=2,
                      font=('TH SarabunPSK',20,'bold'),
                      text_color='black',
                      fg_color='#87BFE5',
                      command=lambda:self.main_frame.show_page('ค้นหาผู้ต้องขัง')
                      ).pack(pady=10)
        
        ctk.CTkButton(self,
                      text='ผู้ต้องขังทั้งหมด',
                      border_color='black',
                      border_width=2,
                      font=('TH SarabunPSK',20,'bold'),
                      text_color='black',
                      fg_color='#87BFE5',
                      command=lambda:self.main_frame.show_page('ผู้ต้องขังทั้งหมด')
                      ).pack(pady=10)
        
        ctk.CTkLabel(self,
                     text='การเยี่ยมญาติ',
                     font=('TH SarabunPSK',28,'bold')
                     ).pack(pady=10)
        
        ctk.CTkButton(self,
                      text='จองเยี่ยมญาติ',
                      border_color='black',
                      border_width=2,
                      font=('TH SarabunPSK',20,'bold'),
                      text_color='black',
                      fg_color='#87BFE5',
                      hover_color='#63FF5B',
                      command=lambda:self.main_frame.show_page('จองเยี่ยม')
                      ).pack(pady=10)
        
        ctk.CTkButton(self,
                      text='รายงาน',
                      border_color='black',
                      border_width=2,
                      font=('TH SarabunPSK',20,'bold'),
                      text_color='black',
                      fg_color='#87BFE5',
                      command=lambda:self.main_frame.show_page('รายงาน')
                      ).pack(pady=10)        
        
        ctk.CTkButton(self,
                      text='ลงทะเบียนลายนิ้วมือ',
                      border_color='black',
                      border_width=2,
                      font=('TH SarabunPSK',20,'bold'),
                      text_color='black',
                      fg_color='#87BFE5',
                      command=lambda:self.main_frame.show_page('ลงทะเบียนลายนิ้วมือ')
                      ).pack(pady=10)
        
        ctk.CTkLabel(self,
                     text='Developer by Mr.Phongchai',
                     font=('TH SatabunPSK',14)
                     ).pack(side='bottom')
        
