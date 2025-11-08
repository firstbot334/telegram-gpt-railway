# check_schema.py — 스키마 상태 확인 도우미
from db import engine

with engine.begin() as conn:
    cols = conn.exec_driver_sql(
        "SELECT column_name, data_type FROM information_schema.columns "
        "WHERE table_name='articles' ORDER BY 1"
    ).fetchall()
    idx  = conn.exec_driver_sql(
        "SELECT indexname, indexdef FROM pg_indexes WHERE tablename='articles' ORDER BY 1"
    ).fetchall()

print("=== COLUMNS ===")
for c in cols:
    print(c)
print("\n=== INDEXES ===")
for i in idx:
    print(i)
