from sqlalchemy import Table, Column, MetaData, Integer, String, Text, DateTime, UniqueConstraint, Index, func

metadata = MetaData()

messages = Table(
    "messages",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("src", String(128), nullable=False),               # source channel
    Column("msg_id", String(64), nullable=False),             # original message id
    Column("url", Text, nullable=True),                       # extracted url (if any)
    Column("title", Text, nullable=True),
    Column("content", Text, nullable=True),
    Column("summary_html", Text, nullable=True),
    Column("hash", String(64), nullable=False),               # sha256(text+url)
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    UniqueConstraint("src","msg_id", name="uq_src_msgid"),
    Index("ix_hash", "hash", unique=True),
    Index("ix_created", "created_at")
)
