import customtkinter as ctk

class MenuFrame(ctk.CTkFrame):
    def __init__(self,parent,main_frame):
        super().__init__(parent, fg_color='#f4f7fa')
        self.grid(row=0, column=0, sticky='nsew')
        self.main_frame = main_frame

        # Modern card container (โครงสร้างเดิม)
        card = ctk.CTkFrame(self, fg_color='#ffffff', corner_radius=24, border_width=0)
        card.pack(padx=40, pady=40, fill='y', expand=True)

        # เพิ่ม scrollbar ด้านขวา (ตกแต่งโมเดิร์น) ซ้อนด้วย place
        scrollbar = ctk.CTkScrollbar(self, orientation='vertical', fg_color='#e3eefa', button_color='#b3d1ff', button_hover_color='#2d3a4b', width=12, corner_radius=8)
        scrollbar.place(relx=1.0, rely=0, relheight=1.0, anchor='ne', x=-10, y=40)
        # หมายเหตุ: Scrollbar นี้เป็น UI เท่านั้น ถ้าอยากให้ scroll ได้จริง ต้องเปลี่ยน card เป็น canvas+frame

        ctk.CTkLabel(card,
            text='เมนูจัดการข้อมูลผู้ต้องขัง',
            font=('TH SarabunPSK', 32, 'bold'),
            text_color='#2d3a4b'
        ).pack(pady=(24, 12))

        def modern_button(text, command, icon=None):
            return ctk.CTkButton(
                card,
                text=text,
                font=('TH SarabunPSK', 22, 'bold'),
                text_color='#2d3a4b',
                fg_color='#e3eefa',
                hover_color='#b3d1ff',
                corner_radius=16,
                height=48,
                border_width=0,
                command=command
            )

        modern_button('ลงทะเบียนผู้ต้องขัง', lambda: self.main_frame.show_page('ลงทะเบียนผู้ต้องขัง')).pack(pady=8, fill='x', padx=32)
        # modern_button('ค้นหาผู้ต้องขัง', lambda: self.main_frame.show_page('ค้นหาผู้ต้องขัง')).pack(pady=8, fill='x', padx=32)
        # modern_button('ย้ายแดน,ปรับชั้น', lambda: self.main_frame.show_page('ย้ายแดน,ปรับชั้น')).pack(pady=8, fill='x', padx=32)
        modern_button('ผู้ต้องขังทั้งหมด', lambda: self.main_frame.show_page('ผู้ต้องขังทั้งหมด')).pack(pady=8, fill='x', padx=32)

        ctk.CTkLabel(card,
            text='เมนูจัดการข้อมูลญาติ',
            font=('TH SarabunPSK', 32, 'bold'),
            text_color='#2d3a4b'
        ).pack(pady=(32, 12))

        modern_button('ญาติทั้งหมด', lambda: self.main_frame.show_page('ญาติทั้งหมด')).pack(pady=8, fill='x', padx=32)
        modern_button('ลงทะเบียนลายนิ้วมือ', lambda: self.main_frame.show_page('ลงทะเบียนลายนิ้วมือ')).pack(pady=8, fill='x', padx=32)


        ctk.CTkLabel(card,
            text='การเยี่ยมญาติ',
            font=('TH SarabunPSK', 32, 'bold'),
            text_color='#2d3a4b'
        ).pack(pady=(32, 12))

        modern_button('จองเยี่ยมญาติ', lambda: self.main_frame.show_page('จองเยี่ยม')).pack(pady=8, fill='x', padx=32)
        modern_button('จองเยี่ยมญาติ\nด้วยเลขบัตรประชาชน', lambda: self.main_frame.show_page('จองเยี่ยมญาติด้วยเลขบัตรประชาชน')).pack(pady=8, fill='x', padx=32)
        modern_button('รายงานประจำวัน', lambda: self.main_frame.show_page('รายงาน')).pack(pady=8, fill='x', padx=32)
        modern_button('รายงานประจำเดือน', lambda: self.main_frame.show_page('')).pack(pady=8, fill='x', padx=32)


        ctk.CTkLabel(card,
            text='Developer by Mr.Phongchai',
            font=('TH SarabunPSK', 14),
            text_color='#a0a0a0'
        ).pack(side='bottom', pady=12)

