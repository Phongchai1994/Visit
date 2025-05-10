import tkinter as tk
from tkinter import ttk, messagebox

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import tempfile
import os
# ลงทะเบียนฟอนต์ภาษาไทย (ต้องมีไฟล์ .ttf อยู ่ในโปรเจกต์)
pdfmetrics.registerFont(TTFont("THSarabun", "THSarabunNew.ttf"))

def print_table():
    try:
        temp_pdf = tempfile.mktemp(".pdf")
        c = canvas.Canvas(temp_pdf, pagesize=landscape(A4))  # ➜ แนวนอน
        width, height = landscape(A4)

        c.setFont("THSarabun", 24)
        c.drawCentredString(width / 2, height - 2 * cm, "รายงานรายชอลาสด")
        c.setFont("THSarabun", 16)

        columns = tree["columns"]
        col_widths = [8 * cm] * len(columns)
        headers = [tree.heading(col)["text"] for col in columns]

        start_x = 2 * cm
        start_y = height - 4 * cm
        row_height = 1.2 * cm
        # หัวตาราง
        y = start_y
        x = start_x
        for i, header in enumerate(headers):
            c.rect(x, y, col_widths[i], row_height, stroke=1, fill=0)
            c.drawString(x + 0.3 * cm, y + 0.35 * cm, header)
            x += col_widths[i]
        # ข้อมูล
        y -= row_height
        for child_id in tree.get_children():
            x = start_x
            values = tree.item(child_id, "values")
            for i, value in enumerate(values):
                c.rect(x, y, col_widths[i], row_height, stroke=1, fill=0)
                text = str(value)
                # ตัวเลขจัดชิดขวา
                if isinstance(value, int) or text.isdigit():
                    text_width = c.stringWidth(text, "THSarabun", 16)
                    c.drawString(x + col_widths[i] - text_width - 0.3 * cm, y + 0.35* cm, text)
                else:
                    c.drawString(x + 0.3 * cm, y + 0.35 * cm, text)
                x += col_widths[i]
            y -= row_height
        c.save()
        os.startfile(temp_pdf, "print")
        messagebox.showinfo("พมพสาเรจ", "สงพมพเรยบรอยแลว")
    except Exception as e:
        messagebox.showerror("ผดพลาด", str(e))
 # GUI
root = tk.Tk()
root.title("พมพรายงานแบบ Landscape พรอมฟอนตไทย")
root.geometry("600x300")
tree = ttk.Treeview(root, columns=("ชอ", "อาย"), show="headings")
tree.heading("ชอ", text="ชอ")
tree.heading("อาย", text="อาย")
tree.pack(fill="both", expand=True)
# ข้อมูลตัวอย่าง
data = [("สมชาย ใจด", 30), ("สมหญง แสนงาม", 25), ("วชย กลาหาญ", 40)]
for item in data:
    tree.insert("", "end", values=item)
btn = tk.Button(root, text="พิมพ์ Landscape + ฟอนตไทย", command=print_table, font=("TH Sarabun New", 14))
btn.pack(pady=10)
root.mainloop()