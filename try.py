import hashlib
from manage.database import SQLiteDB
password = hashlib.sha256(b'123456').digest()
print(password)

db = SQLiteDB()
db.set_execute_manual('UPDATE users SET password = ? WHERE username = ?', (password, 'user'))