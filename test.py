import customtkinter as ctk
import threading
from datetime import datetime
import time as t
import ttkbootstrap as tb

ctk.set_appearance_mode("light")  # หรือ "dark"
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Threading Demo")
app.geometry("300x700")

def fn_test():
    # test_time = round_visit_var.get()
    # round_time = datetime.strptime(test_time,"%H:%M" )
    # date_now = datetime.now().strftime("%d-%m-%Y")
    # print(date_now)
    # print(round_time.strftime("%H:%M"))

    # test_time = '10:30'
    # test_date = '04-05-2025'
    # print((datetime.strptime(test_time,"%H:%M")).strftime("%H:%M"))
    # print(datetime.strftime(test_time,"%H:%M"))
    print(radio_bt_1.get())
    pass

round_visit_var = ctk.StringVar()

ctk.CTkLabel(app,text='เช้า').pack(pady = 10)
# round_1 = ctk.CTkRadioButton(app,text='รอบที่ 1 เวลา 09.30 - 09.45',variable=round_visit_var,value='09:30')
# round_1.pack(pady = 3)
# round_2 = ctk.CTkRadioButton(app,text='รอบที่ 2 เวลา 10.00 - 10.15',variable=round_visit_var,value='10:00')
# round_2.pack(pady = 3)
# round_3 = ctk.CTkRadioButton(app,text='รอบที่ 3 เวลา 10.30 - 10.45',variable=round_visit_var,value='10:30')
# round_3.pack(pady = 3)
# round_4 = ctk.CTkRadioButton(app,text='รอบที่ 4 เวลา 11.00 - 11.15',variable=round_visit_var,value='11:00')
# round_4.pack(pady = 3)

# ctk.CTkLabel(app,text='บ่าย').pack(pady = 10)
# round_5 = ctk.CTkRadioButton(app,text='รอบที่ 5 เวลา 13.15 - 13.30',variable=round_visit_var,value='13:15')
# round_5.pack(pady = 3)
# round_6 = ctk.CTkRadioButton(app,text='รอบที่ 6 เวลา 13.45 - 14.00',variable=round_visit_var,value='13:45')
# round_6.pack(pady = 3)
# round_7 = ctk.CTkRadioButton(app,text='รอบที่ 7 เวลา 14.15 - 14.30',variable=round_visit_var,value='14:15')
# round_7.pack(pady = 3)

radio_bt_1 = ctk.CTkCheckBox(app,text='คนที่ 1')
radio_bt_1.pack()
radio_bt_2 = ctk.CTkCheckBox(app,text='คนที่ 2').pack()
radio_bt_3 = ctk.CTkCheckBox(app,text='คนที่ 3').pack()
radio_bt_4 = ctk.CTkCheckBox(app,text='คนที่ 4').pack()
radio_bt_5 = ctk.CTkCheckBox(app,text='คนที่ 5').pack()
radio_bt_6 = ctk.CTkCheckBox(app,text='คนที่ 6').pack()
radio_bt_7 = ctk.CTkCheckBox(app,text='คนที่ 7').pack()
radio_bt_8 = ctk.CTkCheckBox(app,text='คนที่ 8').pack()
radio_bt_9 = ctk.CTkCheckBox(app,text='คนที่ 9').pack()
radio_bt_10 = ctk.CTkCheckBox(app,text='คนที่ 10').pack()

# my_date = tb.DateEntry(app,bootstyle='danger')
# my_date.pack()

button = ctk.CTkButton(app, text="ทดสอบ", command=fn_test)
button.pack(pady=10)

app.mainloop()
