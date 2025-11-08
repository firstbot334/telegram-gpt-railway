# models.py (autofix version)
import os
import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.orm import declarative_base

# ─────────────────────────────────────────────────────────────────────────────
# On-import DB schema auto-fix (no circular import).
# Uses DATABASE_URL directly to ensure the schema exists before ORM usage.
# This avoids needing psql/bash/extra scripts.
# ─────────────────────────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    try:
        eng = sa.create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
        with eng.begin() as conn:
            # 1) pg_trgm extension for trigram GIN
            conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
            # 2) ensure 'date' column exists
            conn.exec_driver_sql("ALTER TABLE IF EXISTS articles ADD COLUMN IF NOT EXISTS date TIMESTAMPTZ;")
            # 3) drop legacy btree index (problematic for long text)
            conn.exec_driver_sql("DROP INDEX IF EXISTS ix_articles_text;")
            # 4) create GIN(trigram) index for long text & fast search
            conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS ix_articles_text_trgm ON articles USING gin (text gin_trgm_ops);")
    except Exception as _e:
        # Never block app boot; collector/summary can still run.
        pass
    finally:
        try:
            eng.dispose()
        except Exception:
            pass

Base = declarative_base()

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime(timezone=True))
    url = Column(String)
    text = Column(Text)
    summary = Column(Text)

# ORM-level index declaration (won't error if already present because of IF NOT EXISTS above)
Index(
    "ix_articles_text_trgm",
    Article.text,
    postgresql_using="gin",
    postgresql_ops={"text": "gin_trgm_ops"},
)
