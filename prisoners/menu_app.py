import customtkinter as ctk

class MenuFrame(ctk.CTkFrame):
    def __init__(self,parent,main_frame):
        super().__init__(parent, fg_color='#f4f7fa')
        self.grid(row=0, column=0, sticky='nsew')
        self.main_frame = main_frame
        
        # Configure grid weight for responsive design
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create scrollable frame for content
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color='#f4f7fa',
            scrollbar_fg_color='#e3eefa',
            scrollbar_button_color='#b3d1ff',
            scrollbar_button_hover_color='#2d3a4b'
        )
        self.scrollable_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Modern card container
        card = ctk.CTkFrame(self.scrollable_frame, fg_color='#ffffff', corner_radius=24, border_width=0)
        card.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)  # Make the button container expandable

        # Title and content setup
        title_frame = ctk.CTkFrame(card, fg_color='transparent')
        title_frame.grid(row=0, column=0, sticky='ew', padx=32, pady=(24, 12))
        title_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(title_frame,
            text='เมนูจัดการข้อมูลผู้ต้องขัง',
            font=('TH SarabunPSK', 24, 'bold'),
            text_color='#2d3a4b'
        ).pack()

        def modern_button(parent, text, command, icon=None):
            return ctk.CTkButton(
                parent,
                text=text,
                font=('TH SarabunPSK', 20, 'bold'),  # เพิ่มขนาดฟอนต์จาก 22 เป็น 24
                text_color='#2d3a4b',
                fg_color='#e3eefa',
                hover_color='#b3d1ff',
                corner_radius=16,
                height=48,  # เพิ่มความสูงจาก 48 เป็น 52
                border_width=0,
                command=command
            )

        # Create button container with proper padding
        button_container = ctk.CTkFrame(card, fg_color='transparent')
        button_container.grid(row=1, column=0, sticky='nsew', padx=32, pady=20)
        button_container.grid_columnconfigure(0, weight=1)

        # Prisoner management section
        prisoner_section = ctk.CTkFrame(button_container, fg_color='transparent')
        prisoner_section.pack(fill='x', pady=(0, 20))
        
        modern_button(prisoner_section, 'ลงทะเบียนผู้ต้องขัง', lambda: self.main_frame.show_page('ลงทะเบียนผู้ต้องขัง')).pack(pady=4, fill='x')
        # modern_button('ค้นหาผู้ต้องขัง', lambda: self.main_frame.show_page('ค้นหาผู้ต้องขัง')).pack(pady=4, fill='x')
        # modern_button('ย้ายแดน,ปรับชั้น', lambda: self.main_frame.show_page('ย้ายแดน,ปรับชั้น')).pack(pady=4, fill='x')
        modern_button(prisoner_section, 'ผู้ต้องขังทั้งหมด', lambda: self.main_frame.show_page('ผู้ต้องขังทั้งหมด')).pack(pady=4, fill='x')

        ctk.CTkLabel(button_container,
            text='เมนูจัดการข้อมูลญาติ',
            font=('TH SarabunPSK', 24, 'bold'),
            text_color='#2d3a4b'
        ).pack(pady=(12, 12))

        # Relative management section
        relative_section = ctk.CTkFrame(button_container, fg_color='transparent')
        relative_section.pack(fill='x', pady=(0, 20))
        
        modern_button(relative_section, 'ญาติทั้งหมด', lambda: self.main_frame.show_page('ญาติทั้งหมด')).pack(pady=4, fill='x')
        modern_button(relative_section, 'ลงทะเบียนลายนิ้วมือ', lambda: self.main_frame.show_page('ลงทะเบียนลายนิ้วมือ')).pack(pady=4, fill='x')

        ctk.CTkLabel(button_container,
            text='การเยี่ยมญาติ',
            font=('TH SarabunPSK', 24, 'bold'),
            text_color='#2d3a4b'
        ).pack(pady=(12, 12))

        # Visit management section
        visit_section = ctk.CTkFrame(button_container, fg_color='transparent')
        visit_section.pack(fill='x', pady=(0, 20))
        
        modern_button(visit_section, 'จองเยี่ยมญาติ', lambda: self.main_frame.show_page('จองเยี่ยม')).pack(pady=4, fill='x')
        modern_button(visit_section, 'จองเยี่ยมญาติ\nด้วยเลขบัตรประชาชน', lambda: self.main_frame.show_page('จองเยี่ยมญาติด้วยเลขบัตรประชาชน')).pack(pady=4, fill='x')
        modern_button(visit_section, 'รายงานประจำวัน', lambda: self.main_frame.show_page('รายงาน')).pack(pady=4, fill='x')
        modern_button(visit_section, 'รายงานประจำเดือน', lambda: self.main_frame.show_page('')).pack(pady=4, fill='x')
        
        ctk.CTkLabel(button_container,
            text='Developer by Mr.Phongchai',
            font=('TH SarabunPSK', 14),
            text_color='#a0a0a0'
        ).pack(side='bottom', pady=12)

