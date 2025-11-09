from sqlalchemy import MetaData, Table, Column, Integer, String, Text, DateTime, func, UniqueConstraint, Index
metadata = MetaData()
news = Table(
    "news", metadata,
    Column("id", Integer, primary_key=True),
    Column("src", String(256), nullable=False),
    Column("msg_id", String(64), nullable=False),
    Column("text", Text, nullable=False),
    Column("url", Text, nullable=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    UniqueConstraint("src","msg_id", name="uq_src_msg"),
    Index("ix_created_at","created_at"),
)
