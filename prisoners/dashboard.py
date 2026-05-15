import customtkinter as ctk
from datetime import datetime

class DashboardApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ระบบสรุปผลข้อมูลการเยี่ยมผู้ต้องขัง")
        self.geometry("1100x700")
        ctk.set_appearance_mode("dark")

        # --- Main Container ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. Header & Date Picker Row
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="Dashboard สรุปภาพรวมระบบ", font=("TH Sarabun New", 30, "bold"))
        self.title_label.pack(side="left")

        # ส่วนเลือกวันที่ (ในอนาคตแนะนำใช้ tkcalendar เสริมได้)
        self.date_entry = ctk.CTkEntry(self.header_frame, placeholder_text="YYYY-MM-DD")
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.pack(side="right", padx=10)
        
        self.btn_refresh = ctk.CTkButton(self.header_frame, text="ดึงข้อมูล", width=100, command=self.refresh_data)
        self.btn_refresh.pack(side="right")

        # 2. KPI Cards (Grid 3x2)
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.cards_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.create_card(0, 0, "ผู้ต้องขังทั้งหมด", "1,250", "#1f538d")
        self.create_card(0, 1, "ผู้ต้องกักขัง", "45", "#1f538d")
        self.create_card(0, 2, "ผิดวินัย", "12", "#c0392b") # สีแดงเตือน
        
        self.create_card(1, 0, "ญาติทั้งหมดในระบบ", "3,500", "#2ecc71")
        self.create_card(1, 1, "วันนี้: ผู้ต้องขังได้รับเยี่ยม", "85", "#f39c12")
        self.create_card(1, 2, "วันนี้: ญาติเข้าเยี่ยม (คน)", "210", "#f39c12")

        # 3. Bottom Table / Log Area
        self.log_frame = ctk.CTkTextbox(self, height=200)
        self.log_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        self.log_frame.insert("0.0", "ระบบพร้อมใช้งาน... \nแสดงข้อมูลล่าสุด ณ " + datetime.now().strftime("%H:%M:%S"))

    def create_card(self, row, col, title, value, color):
        card = ctk.CTkFrame(self.cards_frame, corner_radius=15, border_width=2, border_color=color)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        lbl_title = ctk.CTkLabel(card, text=title, font=("TH Sarabun New", 20))
        lbl_title.pack(pady=(15, 0))
        
        lbl_value = ctk.CTkLabel(card, text=value, font=("Arial", 40, "bold"), text_color=color)
        lbl_value.pack(pady=(5, 15))

    def refresh_data(self):
        target_date = self.date_entry.get()
        # ตรงนี้ให้ใส่ Logic เชื่อมต่อ Database และรัน SQL ที่ให้ไว้ด้านบน
        # จากนั้นสั่ง update ตัวเลขใน Label
        self.log_frame.insert("end", f"\nกำลังดึงข้อมูลของวันที่: {target_date}...")

if __name__ == "__main__":
    app = DashboardApp()
    app.mainloop()