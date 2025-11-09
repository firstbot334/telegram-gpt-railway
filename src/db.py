from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from .config import settings

def get_engine() -> Engine:
    # Pool_pre_ping to survive Railway connection idling
    return create_engine(settings.DATABASE_URL, pool_pre_ping=True, echo=False, future=True)

def execute_sql(engine: Engine, sql: str):
    with engine.begin() as conn:
        conn.execute(text(sql))
