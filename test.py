from datetime import datetime
import time as t

days = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์","อาทิตย์"]
months = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน",
            "พฤษภาคม","มิถุนายน","กรกฎาคม", "สิงหาคม",
            "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]

current_time = t.localtime()
day = days[current_time.tm_wday]
month = months[current_time.tm_mon - 1]

print(current_time)
print(day)
print(month)