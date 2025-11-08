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
# 기존 BTREE 인덱스 제거, GIN(trigram) 인덱스 사용
# 긴 텍스트 저장 시 btree 한도 초과 오류 방지
Index(
    "ix_articles_text_trgm",
    Article.text,
    postgresql_using="gin",
    postgresql_ops={"text": "gin_trgm_ops"},
)