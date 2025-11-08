# fix_schema.py
# DB 스키마를 안전하게 보정: pg_trgm 확장, date 컬럼 추가, GIN 인덱스 생성
from sqlalchemy import text
from db import engine

sqls = [
    "CREATE EXTENSION IF NOT EXISTS pg_trgm;",
    "ALTER TABLE articles ADD COLUMN IF NOT EXISTS date TIMESTAMPTZ;",
    "DROP INDEX IF EXISTS ix_articles_text;",
    "CREATE INDEX IF NOT EXISTS ix_articles_text_trgm ON articles USING gin (text gin_trgm_ops);",
]

with engine.begin() as conn:
    for s in sqls:
        conn.exec_driver_sql(s)
        print("OK:", s)

print("✅ schema fixed")
