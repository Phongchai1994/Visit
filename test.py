import customtkinter as ctk
import threading
import time

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CTkProgressBar หมุนไม่รู้จบ")
        self.geometry("400x200")

        self.label = ctk.CTkLabel(self, text="คลิกเริ่มโหลด", font=("TH SarabunPSK", 24))
        self.label.pack(pady=10)

        self.progress = ctk.CTkProgressBar(self)
        self.progress.pack(pady=10)
        self.progress.set(0)
        self.progress_running = False

        self.btn = ctk.CTkButton(self, text="โหลดข้อมูล", command=self.start_task)
        self.btn.pack(pady=10)

    def start_task(self):
        self.progress_running = True
        self.progress.set(0)
        self.animate_progress()
        self.label.configure(text="กำลังโหลดข้อมูล...")
        self.btn.configure(state="disabled")

        threading.Thread(target=self.do_long_task, daemon=True).start()

    def animate_progress(self):
        if not self.progress_running:
            return

        current = self.progress.get()
        next_val = (current + 0.01) % 1.0
        self.progress.set(next_val)
        self.after(10, self.animate_progress)  # เรียกซ้ำทุก 10 ms

    def do_long_task(self):
        time.sleep(5)  # สมมุติรอโหลด SQLite
        self.after(0, self.stop_progress)

    def stop_progress(self):
        self.progress_running = False
        self.progress.set(1)
        self.label.configure(text="โหลดเสร็จแล้ว ✅")
        self.btn.configure(state="normal")

if __name__ == "__main__":
    ctk.set_appearance_mode("light")  # หรือ "dark"
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()
