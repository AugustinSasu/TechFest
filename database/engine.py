# owner:POP MIRCEA STEFAN
# CRATE_DATE: 2024-06-20 10:40
# LAST MODIFY_DATE: --
# MODIFY BY: --

#initializare baza de date

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from core.config import settings

engine = create_engine(
    settings.oracle_url(),
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,
)

Base = declarative_base()
