CREATE EXTENSION IF NOT EXISTS pg_trgm;

DROP INDEX IF EXISTS ix_articles_text;

CREATE INDEX IF NOT EXISTS ix_articles_text_trgm
  ON articles
  USING gin (text gin_trgm_ops);
