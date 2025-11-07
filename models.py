from sqlalchemy import Column, Integer, Text, DateTime, String
from db import Base

class Article(Base):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text, nullable=False, index=True)
    url = Column(String(500), nullable=True)
    created_at = Column(DateTime, nullable=False)
