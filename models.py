from sqlalchemy import Column, Integer, String, Text, DateTime, BigInteger, ForeignKey, Date, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db import Base

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    url = Column(Text)
    source = Column(String(128))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), unique=True, nullable=False)
    aliases = Column(ARRAY(String), default=[])

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)
    event_date = Column(Date, nullable=False, index=True)
    event_type = Column(String(128))
    headline = Column(Text, nullable=False)
    source_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company")

class PinnedMessage(Base):
    __tablename__ = "pinned_messages"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), unique=True)
    chat_id = Column(String(128), nullable=False)
    message_id = Column(BigInteger, nullable=False)
    last_rendered_at = Column(DateTime(timezone=True))
