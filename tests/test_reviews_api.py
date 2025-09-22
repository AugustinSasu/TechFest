# owner:POP MIRCEA STEFAN
# CRATE_DATE: 2024-06-20 10:40
# LAST MODIFY_DATE: --
# MODIFY BY: --
import datetime as dt
import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# ---- importuri din aplicație ----
from api.routes import review as review_module
from database.engine import Base
from database.session import get_db as app_get_db  # doar pentru typing/override
from models.dealership import Dealership
from models.employee import Employee


# =========================
# FIXTURE: ENGINE & SCHEMA
# =========================
@pytest.fixture(scope="session")
def test_engine():
    """
    SQLite in-memory pentru toată sesiunea, cu foreign_keys activ.
    Folosim StaticPool ca să partajăm aceeași memorie între conexiuni.
    """
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )

    @event.listens_for(engine, "connect")
    def _fk_on(dbapi_conn, _):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    # creează schema (asigură-te că modelele Employee/Dealership/Review sunt importate)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session(test_engine):
    """
    O sesiune proaspătă per test; facem rollback la final pentru izolare.
    """
    SessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False, future=True, expire_on_commit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture()
def client(db_session):
    """
    App FastAPI minimală ce include DOAR router-ul de review-uri
    + override pentru dependency-ul get_db din modulul routerului.
    """
    app = FastAPI()
    app.include_router(review_module.router, prefix="/api")

    def override_get_db():
        yield db_session

    # IMPORTANT: override pe exact dependency-ul folosit de routerul nostru
    app.dependency_overrides[review_module.get_db] = override_get_db
    return TestClient(app)


# =========================
# HELPERE DE SEED
# =========================
def seed_dealership(db, name="D1"):
    d = Dealership(name=name, city="City", region="Region")
    db.add(d)
    db.flush()
    return d

def seed_employee(db, dealership, username, full_name, role_code="SALES", password="pw"):
    e = Employee(
        db_username=username,
        full_name=full_name,
        role_code=role_code,
        dealership_id=dealership.dealership_id,
        password=password,
    )
    db.add(e)
    db.flush()
    return e

def seed_staff_pair(db):
    """
    Creează un dealer + un manager + un salesperson (toate câmpurile minime necesare).
    Returnează (manager, salesperson).
    """
    d = seed_dealership(db, "MainDealer")
    manager = seed_employee(db, d, "mgr_alex", "Alex Manager", role_code="MANAGER", password="x")
    sales   = seed_employee(db, d, "sls_iris", "Iris Sales",    role_code="SALES",   password="y")
    return manager, sales


# =========================
# TESTE CRUD
# =========================
def test_create_review_success(client, db_session):
    manager, sales = seed_staff_pair(db_session)
    payload = {
        "manager_id": manager.employee_id,
        "salesperson_id": sales.employee_id,
        "review_text": "Great quarter performance",
        # lăsăm review_date None pentru a testa default-ul din DB
    }
    r = client.post("/api/reviews", json=payload)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["review_id"] > 0
    assert body["manager_id"] == manager.employee_id
    assert body["salesperson_id"] == sales.employee_id
    assert body["review_text"] == "Great quarter performance"
    # review_date e setat de DB (string ISO), doar verificăm existența
    assert "review_date" in body and body["review_date"]


def test_get_review_404(client):
    r = client.get("/api/reviews/999999")
    assert r.status_code == 404


def test_update_review_success(client, db_session):
    manager, sales = seed_staff_pair(db_session)
    # create
    r1 = client.post("/api/reviews", json={
        "manager_id": manager.employee_id,
        "salesperson_id": sales.employee_id,
        "review_text": "Initial"
    })
    assert r1.status_code == 201
    rid = r1.json()["review_id"]

    # update text + (opțional) data
    new_date = dt.date(2024, 5, 20).isoformat()
    r2 = client.put(f"/api/reviews/{rid}", json={"review_text": "Updated text", "review_date": new_date})
    assert r2.status_code == 200
    body = r2.json()
    assert body["review_text"] == "Updated text"
    assert body["review_date"] == new_date


def test_delete_review_then_404(client, db_session):
    manager, sales = seed_staff_pair(db_session)
    r1 = client.post("/api/reviews", json={
        "manager_id": manager.employee_id,
        "salesperson_id": sales.employee_id,
        "review_text": "To be deleted"
    })
    rid = r1.json()["review_id"]
    r_del = client.delete(f"/api/reviews/{rid}")
    assert r_del.status_code == 204
    r_get = client.get(f"/api/reviews/{rid}")
    assert r_get.status_code == 404


# =========================
# TESTE LISTARE / FILTRE / SORT / PAGINARE
# =========================
def seed_reviews_mixed(client, db_session, count=5):
    """
    Creează un manager, un salesperson și câteva review-uri cu date diferite,
    plus încă un salesperson cu alte review-uri ca să verificăm filtrarea.
    Returnează (manager, s1, s2, ids_s1_sorted_desc_by_date)
    """
    manager, s1 = seed_staff_pair(db_session)
    # al doilea salesperson (same manager, altă persoană)
    d = seed_dealership(db_session, "OtherDealer")
    s2 = seed_employee(db_session, d, "sls_ben", "Ben Sales", role_code="SALES", password="z")

    # Review-uri pentru s1 cu date prestabilite
    dates = [dt.date(2024, 1, 10), dt.date(2024, 2, 5), dt.date(2024, 3, 25), dt.date(2024, 3, 30)]
    ids_s1 = []
    for i, dd in enumerate(dates, start=1):
        r = client.post("/api/reviews", json={
            "manager_id": manager.employee_id,
            "salesperson_id": s1.employee_id,
            "review_text": f"R{i} for s1 on {dd.isoformat()}",
            "review_date": dd.isoformat(),
        })
        assert r.status_code == 201
        ids_s1.append(r.json()["review_id"])

    # Un review pentru s2 (ca să existe și alte înregistrări)
    r_other = client.post("/api/reviews", json={
        "manager_id": manager.employee_id,
        "salesperson_id": s2.employee_id,
        "review_text": "R_for_s2",
        "review_date": dt.date(2024, 4, 15).isoformat(),
    })
    assert r_other.status_code == 201

    # ordinea desc după review_date pentru s1 (dacă două date egale, va decide review_id desc)
    ids_s1_desc = list(reversed(ids_s1))  # pentru date strict crescătoare, id-urile cresc și ele
    return manager, s1, s2, ids_s1_desc


def test_list_by_salesperson_desc(client, db_session):
    _, s1, _, ids_desc_expect = seed_reviews_mixed(client, db_session)

    r = client.get(f"/api/reviews/by-salesperson/{s1.employee_id}")
    assert r.status_code == 200
    body = r.json()
    got_ids = [it["review_id"] for it in body]
    # trebuie să fie desc după review_date (și id desc ca tie-breaker)
    assert got_ids == ids_desc_expect


def test_list_filters_sort_pagination(client, db_session):
    manager, s1, s2, _ = seed_reviews_mixed(client, db_session)

    # filtrare după salesperson_id
    r1 = client.get(f"/api/reviews?salesperson_id={s1.employee_id}&sort=desc")
    assert r1.status_code == 200
    assert all(it["salesperson_id"] == s1.employee_id for it in r1.json())

    # filtrare după manager_id
    r2 = client.get(f"/api/reviews?manager_id={manager.employee_id}")
    assert r2.status_code == 200
    assert all(it["manager_id"] == manager.employee_id for it in r2.json())

    # filtrare după interval de dată
    r3 = client.get("/api/reviews?date_from=2024-02-01&date_to=2024-03-31")
    assert r3.status_code == 200
    body3 = r3.json()
    assert len(body3) >= 1
    for it in body3:
        assert "2024-02-01" <= it["review_date"] <= "2024-03-31"

    # căutare text (q) – insensibilă la caz (ilike)
    r4 = client.get("/api/reviews?q=s1 on 2024-03")
    assert r4.status_code == 200
    assert any("2024-03" in it["review_text"] for it in r4.json())

    # sort explicit asc/desc
    r5 = client.get("/api/reviews?sort_by=review_date&sort=asc")
    assert r5.status_code == 200
    dates = [it["review_date"] for it in r5.json()]
    assert dates == sorted(dates)

    r6 = client.get("/api/reviews?sort_by=review_date&sort=desc")
    assert r6.status_code == 200
    dates_desc = [it["review_date"] for it in r6.json()]
    assert dates_desc == sorted(dates_desc, reverse=True)

    # paginare
    r7 = client.get("/api/reviews?sort=asc&skip=1&limit=2")
    assert r7.status_code == 200
    assert len(r7.json()) == 2
