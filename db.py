from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "")

def _ensure_ssl(url: str) -> str:
    if url and "postgres" in url and "sslmode=" not in url:
        joiner = "&" if "?" in url else "?"
        return f"{url}{joiner}sslmode=require"
    return url

engine = create_engine(_ensure_ssl(DATABASE_URL))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def create_tables():
    import models  # noqa: F401
    Base.metadata.create_all(engine)
