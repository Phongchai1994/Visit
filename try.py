from manage.database import SQLiteDB


db = SQLiteDB()

query = """
            SELECT
                r.relative_id,
                r.title,
                r.f_name,
                r.l_name,
                r.address,
                r.tel,
                rel.relation
            FROM relations rel
            JOIN relatives r ON rel.relative_id = r.relative_id
            WHERE rel.prisoner_id = 6530800007
        """
id = 6530800007
# data = db.execute_manual(query)
data = db.get_join_prisoners_and_relatives(id)

print(data)
