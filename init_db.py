#!/usr/bin/env python3
"""
Initialize Neon PostgreSQL database.
Run once after setting DATABASE_URL to your Neon connection string.
"""
import os
from sqlalchemy import create_engine
from app.database import Base
from app.models import User, Calendar, Event

def init_db():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError(
            "DATABASE_URL not set. Set to your Neon connection string: "
            "postgresql://user:pass@host/dbname"
        )
    engine = create_engine(db_url, echo=True)
    Base.metadata.create_all(bind=engine)
    print("Tables created in Neon.")
    print("Next: set SECRET_KEY env var, run uvicorn app.main:app --reload")

if __name__ == "__main__":
    init_db()