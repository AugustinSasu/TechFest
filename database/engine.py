from sqlalchemy import create_engine
from core.config import settings
engine = create_engine(settings.oracle_url(), echo=False, pool_pre_ping=True, pool_size=5, max_overflow=10)