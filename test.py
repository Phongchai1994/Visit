import customtkinter as ctk
import threading
import time

ctk.set_appearance_mode("light")  # หรือ "dark"
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Threading Demo")
app.geometry("300x200")

label = ctk.CTkLabel(app, text="ยังไม่เริ่ม", font=("TH SarabunPSK", 30))
label.pack(pady=20)

def count_in_thread():
    def run():
        for i in range(5):
            time.sleep(1)
            # อัปเดต label จาก main thread ด้วย .after()
            label.after(0, lambda i=i: label.configure(text=f"นับ: {i+1}"))
        label.after(0, lambda: label.configure(text="เสร็จแล้ว!"))

    threading.Thread(target=run,daemon=True).start()

button = ctk.CTkButton(app, text="เริ่มนับ", command=count_in_thread)
button.pack(pady=10)

app.mainloop()
