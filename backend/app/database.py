import os
import warnings
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQLITE_FALLBACK_URL = "sqlite:///./shakti360.db"


def normalized_database_url(raw: str | None) -> str:
    value = (raw or "").strip().strip("'\"")
    if not value or value.startswith("${{"):
        if value:
            warnings.warn("DATABASE_URL is an unresolved service reference; using local SQLite.", RuntimeWarning)
        return SQLITE_FALLBACK_URL
    if value.startswith("postgres://"):
        value = value.replace("postgres://", "postgresql://", 1)
    if value.startswith("postgresql://"):
        value = value.replace("postgresql://", "postgresql+psycopg://", 1)
    try:
        make_url(value)
    except ArgumentError:
        warnings.warn("DATABASE_URL is malformed; using local SQLite. Correct the Railway database reference for persistent storage.", RuntimeWarning)
        return SQLITE_FALLBACK_URL
    return value


DATABASE_URL = normalized_database_url(os.getenv("DATABASE_URL"))
# Zerops exposes a standard postgresql:// connection string. This project uses
# Psycopg 3, so select SQLAlchemy's psycopg dialect explicitly.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
