# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Shared declarative base for all models
Base = declarative_base()

# Lazy-loaded engine - created on first use
_engine = None
_SessionLocal = None

def get_engine():
    global _engine
    if _engine is None:
        SQLALCHEMY_DATABASE_URL = os.getenv(
            "DATABASE_URL",
            "postgresql://user:***@host/dbname"
        )
        # Use pg8000 dialect for pure Python PostgreSQL driver
        if SQLALCHEMY_DATABASE_URL.startswith("postgresql://"):
            SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgresql://", "postgresql+pg8000://", 1)
        _engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
    return _engine

def get_session_local():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal

def get_db():
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()