
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from database.engine import engine

class Base(DeclarativeBase):
    pass

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)