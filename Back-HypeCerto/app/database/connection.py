"""
database/connection.py
Conexão com Supabase (PostgreSQL) via SQLAlchemy.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency: fornece sessão de banco de dados e garante fechamento."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
