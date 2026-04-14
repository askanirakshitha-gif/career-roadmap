"""
database.py — Connects FastAPI to PostgreSQL using SQLAlchemy.

HOW IT WORKS:
  1. We read the DATABASE_URL from your .env file
  2. SQLAlchemy creates a connection "engine" (like a phone line to DB)
  3. SessionLocal creates individual "calls" (sessions) for each request
  4. get_db() is a "dependency" — FastAPI calls it automatically for each route

DATABASE_URL FORMAT:
  postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE_NAME

  Example (local):  postgresql://postgres:mypassword@localhost:5432/career_roadmap
  Example (Supabase): postgresql://postgres:mypassword@db.xxxx.supabase.co:5432/postgres
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
from pathlib import Path

# Load variables from the .env file located next to this file so the DB
# configuration is deterministic regardless of the process working directory.
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=str(env_path))

DATABASE_URL = os.getenv("DATABASE_URL")

# If DATABASE_URL isn't set, fall back to a local SQLite DB for development.
# This makes it easier to run the API locally without a Postgres instance.
if not DATABASE_URL:
    # Use a file-based SQLite DB in the backend folder for quick local testing
    DATABASE_URL = "sqlite:///./dev.db"
    print(
        "Warning: DATABASE_URL not found in .env — using local SQLite dev.db for development.\n"
        "To use PostgreSQL, create backend/.env with: DATABASE_URL=postgresql://user:pass@host:port/dbname"
    )

# Engine = the actual connection to PostgreSQL
engine = create_engine(
    DATABASE_URL,
    # SQLite requires a special connect_args when used with threads/async servers
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,   # Test connection before using it
    echo=False,           # Set True to see SQL queries in terminal (useful for debugging)
)

# SessionLocal = factory for database sessions (one per request)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = parent class for all our database models (tables)
Base = declarative_base()


def get_db():
    """
    FastAPI dependency — provides a DB session to each route.
    Automatically closes the session when the request is done.
    
    Usage in routes:
        def my_route(db: Session = Depends(get_db)):
    """
    db = SessionLocal()
    try:
        yield db          # Give the session to the route
    finally:
        db.close()        # Always close when done (prevents connection leaks)