import sqlite3
import psycopg2

SQLITE_DB = 'visit_report.db'
PG_HOST = "192.168.1.144"
PG_PORT = "5432"
PG_NAME = "report_visit"
PG_USER = "postgres"
PG_PASS = "Pkt190994"

TABLES_INFO = [
    {"name": "prisoners_", "pk": "prisoner_id", "has_serial": False},
    {"name": "relatives", "pk": "relative_id", "has_serial": False},
    {"name": "users", "pk": "id", "has_serial": True},
    {"name": "holidays", "pk": "id", "has_serial": True},
    {"name": "check_", "pk": "id", "has_serial": True},
    {"name": "relations", "pk": "id", "has_serial": True},
    {"name": "visits", "pk": "visit_id", "has_serial": True},
    {"name": "visit_history", "pk": "id", "has_serial": True},
    {"name": "visit_spacial", "pk": "visit_id", "has_serial": True},
    {"name": "log_realtime", "pk": "id", "has_serial": True},
    {"name": "log_error", "pk": "log_id", "has_serial": True}
]

def clean_data(rows):
    """
    ฟังก์ชันสำหรับทำความสะอาดข้อมูล:
    ถ้าเจอค่าที่เป็นช่องว่าง '' ให้เปลี่ยนเป็น None (เพื่อกลายเป็น NULL ใน PostgreSQL)
    """
    cleaned_rows = []
    for row in rows:
        cleaned_row = []
        for val in row:
            if val == "":
                cleaned_row.append(None)
            else:
                cleaned_row.append(val)
        cleaned_rows.append(tuple(cleaned_row))
    return cleaned_rows

def migrate_data_safe():
    try:
        sl_conn = sqlite3.connect(SQLITE_DB)
        sl_cursor = sl_conn.cursor()
        
        pg_conn = psycopg2.connect(host=PG_HOST, port=PG_PORT, database=PG_NAME, user=PG_USER, password=PG_PASS)
        pg_cursor = pg_conn.cursor()
        
        print("🚀 เริ่มกระบวนการดึงข้อมูล (Clean Data Mode)...")

        for table_data in TABLES_INFO:
            table = table_data["name"]
            pk = table_data["pk"]
            has_serial = table_data["has_serial"]
            
            print(f"กำลังย้ายข้อมูลตาราง: {table} ...", end=" ")
            
            sl_cursor.execute(f'SELECT * FROM "{table}"')
            raw_rows = sl_cursor.fetchall()
            
            if not raw_rows:
                print("-> ไม่มีข้อมูล")
                continue

            # ทำความสะอาดข้อมูลก่อนยัด (ล้างช่องว่างเป็น NULL)
            rows = clean_data(raw_rows)

            col_names = [desc[0] for desc in sl_cursor.description]
            cols_str = ', '.join([f'"{col}"' for col in col_names])
            placeholders = ', '.join(['%s'] * len(col_names))
            
            insert_query = f"""
                INSERT INTO "{table}" ({cols_str}) 
                VALUES ({placeholders}) 
                ON CONFLICT ("{pk}") DO NOTHING
            """

            try:
                # ลองยัดเข้าไปทีเดียวรวด
                pg_cursor.executemany(insert_query, rows)
                pg_conn.commit()
                print(f"✅ สำเร็จ {pg_cursor.rowcount} รายการ")

            except psycopg2.Error as e:
                pg_conn.rollback()
                print(f"\n   ⚠️ พบข้อมูลขยะในตาราง {table}: {e}")
                print(f"   -> ระบบจะพยายามยัดข้อมูลทีละบรรทัด (เพื่อข้ามข้อมูลที่มีปัญหา)...")
                
                # ถ้ายัดทีเดียวรวดแล้วพัง ให้ลองยัดทีละบรรทัด (อันไหนพังก็ข้ามไป)
                success_count = 0
                error_count = 0
                for row in rows:
                    try:
                        pg_cursor.execute(insert_query, row)
                        pg_conn.commit()
                        success_count += 1
                    except psycopg2.Error:
                        pg_conn.rollback() # ข้ามบรรทัดนี้ไป
                        error_count += 1
                print(f"   ✅ กู้สำเร็จ {success_count} รายการ | ❌ ข้ามข้อมูลขยะไป {error_count} รายการ")

            # อัปเดต Sequence
            if has_serial:
                pg_cursor.execute(f"SELECT setval('\"{table}_{pk}_seq\"', COALESCE((SELECT MAX({pk}) FROM \"{table}\"), 1), true)")
                pg_conn.commit()

        print("\n🎉 ย้ายข้อมูลสำเร็จทั้งหมดแล้ว!")

    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
    finally:
        if 'sl_conn' in locals() and sl_conn: sl_conn.close()
        if 'pg_conn' in locals() and pg_conn: pg_conn.close()

if __name__ == "__main__":
    migrate_data_safe()