from sqlalchemy import Table, Column, MetaData, Integer, String, Text, DateTime, UniqueConstraint, Index, func
metadata = MetaData()
messages = Table('messages', metadata,
    Column('id', Integer, primary_key=True),
    Column('src', String(256), nullable=False),
    Column('msg_id', String(64), nullable=False),
    Column('url', Text, nullable=True),
    Column('title', Text, nullable=True),
    Column('content', Text, nullable=True),
    Column('summary_html', Text, nullable=True),
    Column('hash', String(64), nullable=False),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    UniqueConstraint('src','msg_id', name='uq_src_msgid'),
    Index('ix_hash','hash', unique=True),
    Index('ix_created','created_at')
)
