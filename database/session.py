from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import text
from core.config import settings
from .engine import engine

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

def get_db() -> Session:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
