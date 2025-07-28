# 6530800007

from manage.database import SQLiteDB

db = SQLiteDB()

prisoner_id = str(6530800007)
relative_id = str(1560100345135)
date = str('2025-07-25')
query = f'SELECT count (*) FROM visits WHERE date_visit = "2025-07-25"'
data_db = db.get_join_relatives_and_prisoners(relative_id)

print(data_db)