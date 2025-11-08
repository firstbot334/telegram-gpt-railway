# sitecustomize.py (defensive schema autofix on process start)
import os
import sqlalchemy as sa

DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    try:
        eng = sa.create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
        with eng.begin() as conn:
            conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
            conn.exec_driver_sql("CREATE TABLE IF NOT EXISTS articles (id SERIAL PRIMARY KEY);")
            conn.exec_driver_sql("ALTER TABLE articles ADD COLUMN IF NOT EXISTS date TIMESTAMPTZ;")
            conn.exec_driver_sql("ALTER TABLE articles ADD COLUMN IF NOT EXISTS url VARCHAR;")
            conn.exec_driver_sql("ALTER TABLE articles ADD COLUMN IF NOT EXISTS text TEXT;")
            conn.exec_driver_sql("ALTER TABLE articles ADD COLUMN IF NOT EXISTS summary TEXT;")
            conn.exec_driver_sql("ALTER TABLE articles ADD COLUMN IF NOT EXISTS source VARCHAR;")
            conn.exec_driver_sql("DROP INDEX IF EXISTS ix_articles_text;")
            conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS ix_articles_text_trgm ON articles USING gin (text gin_trgm_ops);")
    except Exception:
        pass
    finally:
        try:
            eng.dispose()
        except Exception:
            pass
