from sqlalchemy import create_engine, text

from core.config import settings

url = settings.oracle_url()
engine = create_engine(url, echo=True, pool_pre_ping=True)

with engine.connect() as conn:
    # (opțional) dacă NU te loghezi ca APP_OWNER, setează schema curentă:
    # conn.execute(text("ALTER SESSION SET CURRENT_SCHEMA=APP_OWNER"))

    # vezi ce tabele ai
    rows = conn.execute(text("""
        SELECT table_name
        FROM user_tables
        ORDER BY table_name
    """)).fetchall()
    print(rows)

    # testează un SELECT simplu pe una din tabelele tale:
    rows = conn.execute(text("SELECT name, city FROM dealership FETCH FIRST 5 ROWS ONLY")).fetchall()
    print(rows)
