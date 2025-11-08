from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime(timezone=True))
    url = Column(String)
    text = Column(Text)
    summary = Column(Text)

# ────────────────────────────────────────────────
# BTREE → GIN(trigram) 인덱스로 전환 (긴 텍스트 안전 + 검색 빠름)
Index(
    "ix_articles_text_trgm",
    Article.text,
    postgresql_using="gin",
    postgresql_ops={"text": "gin_trgm_ops"},
)
