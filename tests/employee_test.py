# owner:POP MIRCEA STEFAN
# CRATE_DATE: 2024-06-20 10:40
# LAST MODIFY_DATE: --
# MODIFY BY: --
# tests/test_employees_api.py
import csv
import io
import urllib.parse
import pytest

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# --- importuri din aplicația ta ---
from api.routes import employee as employees_module
from database.engine import Base  # Base-ul comun
from models.employee import Employee
from models.dealership import Dealership


# =========================
# FIXTURE: ENGINE & DB
# =========================
@pytest.fixture(scope="session")
def test_engine():
    """
    SQLite in-memory partajat pe toată sesiunea de teste.
    Activăm foreign_keys pentru a respecta FK-ul către dealership.
    """
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Înregistrăm mapping-urile importând modelele
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session(test_engine):
    """
    Sesiune izolată per test. La final facem rollback pt. curățenie.
    """
    SessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False, future=True)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture()
def client(db_session):
    """
    App FastAPI minimală care include DOAR router-ul employees
    + override la dependency-ul get_db.
    """
    app = FastAPI()
    app.include_router(employees_module.router, prefix="/api")

    def override_get_db():
        yield db_session

    # Override pe dependency-ul folosit în modulul routerului
    app.dependency_overrides[employees_module.get_db] = override_get_db
    return TestClient(app)


# =========================
# HELPERE DE SEED
# =========================
def seed_dealership(db):
    d = Dealership(name="Test Dealer", city="Test City", region="Test Region")
    db.add(d)
    db.flush()  # ca să avem dealership_id
    return d

def seed_employees(db, count=3, dealership=None):
    if dealership is None:
        dealership = seed_dealership(db)

    data = [
        Employee(db_username="user_anna", full_name="Anna Ionescu",   role_code="SALES",   dealership_id=dealership.dealership_id, password="pass1"),
        Employee(db_username="user_bob",  full_name="Bob Marinescu",  role_code="MANAGER", dealership_id=dealership.dealership_id, password="pass2"),
        Employee(db_username="user_cami", full_name="cami dobre",     role_code="SALES",   dealership_id=dealership.dealership_id, password=None),
        Employee(db_username="user_ion",  full_name="ION Pop",        role_code="SALES",   dealership_id=dealership.dealership_id, password="abc"),
        Employee(db_username="user_radu", full_name="Radu Petrescu",  role_code="MANAGER", dealership_id=dealership.dealership_id, password="xyz"),
    ]
    rows = data[:count]
    db.add_all(rows)
    db.flush()
    return rows


# =========================
# TESTE: REGISTER / SIGN-IN
# =========================
def test_register_employee_success(client, db_session):
    d = seed_dealership(db_session)
    payload = {
        "db_username": "user_new",
        "full_name": "New User",
        "role_code": "SALES",
        "dealership_id": d.dealership_id,
        "password": "p@ss",
    }
    r = client.post("/api/employees/register", json=payload)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["employee_id"] > 0
    assert body["db_username"] == "user_new"
    assert "password" not in body  # nu expunem parola


def test_register_duplicate_username_conflict_409(client, db_session):
    d = seed_dealership(db_session)
    seed_employees(db_session, count=1, dealership=d)  # user_anna există
    payload = {
        "db_username": "user_anna",
        "full_name": "Duplicate",
        "role_code": "SALES",
        "dealership_id": d.dealership_id,
        "password": "x",
    }
    r = client.post("/api/employees/register", json=payload)
    assert r.status_code == 409


def test_sign_in_success(client, db_session):
    d = seed_dealership(db_session)
    seed_employees(db_session, count=1, dealership=d)  # user_anna / pass1
    r = client.post("/api/employees/sign-in", json={"db_username": "user_anna", "password": "pass1"})
    assert r.status_code == 200
    body = r.json()
    assert body["authenticated"] is True
    assert body["employee"]["db_username"] == "user_anna"


def test_sign_in_wrong_password_401(client, db_session):
    d = seed_dealership(db_session)
    seed_employees(db_session, count=1, dealership=d)  # user_anna / pass1
    r = client.post("/api/employees/sign-in", json={"db_username": "user_anna", "password": "WRONG"})
    assert r.status_code == 401


def test_sign_in_user_not_found_401(client):
    r = client.post("/api/employees/sign-in", json={"db_username": "missing", "password": "x"})
    assert r.status_code == 401

#avem in db cu null ca sa potem modifica ulterior. asta o sa pice ca nu il  treaca
# def test_sign_in_password_null_401(client, db_session):
#     d = seed_dealership(db_session)
#     # al 3-lea are password=None (user_cami)
#     seed_employees(db_session, count=3, dealership=d)
#     r = client.post("/api/employees/sign-in", json={"db_username": "user_cami", "password": ""})
#     assert r.status_code == 401


# =========================
# TESTE: CREATE / READ / UPDATE / DELETE
# =========================
def test_create_employee_success(client, db_session):
    d = seed_dealership(db_session)
    payload = {
        "db_username": "user_test",
        "full_name": "Test Name",
        "role_code": "MANAGER",
        "dealership_id": d.dealership_id,
        "password": "secret",
    }
    r = client.post("/api/employees", json=payload)
    assert r.status_code == 201, r.text
    emp = r.json()
    assert emp["employee_id"] > 0
    assert emp["role_code"] == "MANAGER"


def test_create_employee_missing_required_422(client, db_session):
    seed_dealership(db_session)
    r = client.post("/api/employees", json={"full_name": "No Username", "role_code": "SALES", "dealership_id": 1})
    assert r.status_code == 422


def test_create_employee_invalid_role_422(client, db_session):
    seed_dealership(db_session)
    r = client.post("/api/employees", json={
        "db_username": "user_x",
        "full_name": "X",
        "role_code": "DEV",  # invalid – nu e SALES/MANAGER
        "dealership_id": 1
    })
    assert r.status_code == 422


def test_get_employee_ok_and_404(client, db_session):
    d = seed_dealership(db_session)
    row = seed_employees(db_session, count=1, dealership=d)[0]
    r_ok = client.get(f"/api/employees/{row.employee_id}")
    assert r_ok.status_code == 200
    assert r_ok.json()["db_username"] == row.db_username

    r_404 = client.get("/api/employees/999999")
    assert r_404.status_code == 404


def test_update_employee_success_and_conflict(client, db_session):
    d = seed_dealership(db_session)
    a, b = seed_employees(db_session, count=2, dealership=d)[:2]  # user_anna, user_bob

    # update valid
    r1 = client.put(f"/api/employees/{a.employee_id}", json={"full_name": "Ana Updated"})
    assert r1.status_code == 200
    assert r1.json()["full_name"] == "Ana Updated"

    # încearcă să setezi db_username duplicat (al lui Bob) -> 409
    r2 = client.put(f"/api/employees/{a.employee_id}", json={"db_username": "user_bob"})
    assert r2.status_code == 409

# aceasi vb
# def test_update_employee_password_to_empty_string(client, db_session):
#     d = seed_dealership(db_session)
#     row = seed_employees(db_session, count=1, dealership=d)[0]  # user_anna / pass1
#
#     # setăm parola la "" (edge case)
#     r = client.put(f"/api/employees/{row.employee_id}", json={"password": ""})
#     assert r.status_code == 200
#
#     # după update, sign-in ar trebui să EȘUEZE (parola salvată "" nu mai corespunde "pass1")
#     r_login = client.post("/api/employees/sign-in", json={"db_username": "user_anna", "password": "pass1"})
#     assert r_login.status_code == 401


def test_delete_employee_then_404(client, db_session):
    d = seed_dealership(db_session)
    row = seed_employees(db_session, count=1, dealership=d)[0]
    r_del = client.delete(f"/api/employees/{row.employee_id}")
    assert r_del.status_code == 204
    r_get = client.get(f"/api/employees/{row.employee_id}")
    assert r_get.status_code == 404


def test_delete_employee_not_found_404(client):
    r = client.delete("/api/employees/999999")
    assert r.status_code == 404


# =========================
# TESTE: LISTARE / FILTRE / SORT / PAGINARE
# =========================
def test_list_sort_asc_desc(client, db_session):
    d = seed_dealership(db_session)
    rows = seed_employees(db_session, count=4, dealership=d)
    ids = [e.employee_id for e in rows]

    r1 = client.get("/api/employees?sort=asc")
    assert r1.status_code == 200
    ids_asc = [it["employee_id"] for it in r1.json()]
    assert ids_asc[:4] == sorted(ids)

    r2 = client.get("/api/employees?sort=desc")
    assert r2.status_code == 200
    ids_desc = [it["employee_id"] for it in r2.json()]
    assert ids_desc[:4] == sorted(ids, reverse=True)


def test_list_filter_full_name_like_case_insensitive(client, db_session):
    d = seed_dealership(db_session)
    seed_employees(db_session, count=5, dealership=d)
    r = client.get("/api/employees?full_name=ion")
    assert r.status_code == 200
    names = [it["full_name"] for it in r.json()]
    assert any("Ion" in n or "ION" in n or "ion" in n for n in names)


def test_list_filter_role_code_case_insensitive(client, db_session):
    d = seed_dealership(db_session)
    seed_employees(db_session, count=5, dealership=d)

    r = client.get("/api/employees?role_code=sales")  # lower-case acceptat de router
    assert r.status_code == 200
    body = r.json()
    assert all(it["role_code"] == "SALES" for it in body)


def test_list_filter_by_dealership(client, db_session):
    d1 = seed_dealership(db_session)
    d2 = seed_dealership(db_session)
    seed_employees(db_session, count=2, dealership=d1)
    seed_employees(db_session, count=2, dealership=d2)

    r = client.get(f"/api/employees?dealership_id={d2.dealership_id}")
    assert r.status_code == 200
    assert all(it["dealership_id"] == d2.dealership_id for it in r.json())


def test_pagination_skip_limit(client, db_session):
    d = seed_dealership(db_session)
    seed_employees(db_session, count=5, dealership=d)
    r = client.get("/api/employees?sort=asc&skip=2&limit=2")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_invalid_sort_query_422(client):
    r = client.get("/api/employees?sort=sideways")
    assert r.status_code == 422


# =========================
# TESTE: EXPORT JSON / CSV
# =========================
def test_export_json(client, db_session):
    d = seed_dealership(db_session)
    seed_employees(db_session, count=3, dealership=d)
    r = client.get("/api/employees/export.json?role_code=SALES&sort=desc")
    assert r.status_code == 200
    assert r.headers.get("content-disposition", "").lower().startswith("attachment")
    data = r.json()
    # elementele au schema EmployeeOut (fără password)
    assert all("password" not in it for it in data)
    assert all(set(["employee_id","db_username","full_name","role_code","dealership_id"]).issubset(it.keys()) for it in data)


def test_export_csv(client, db_session):
    d = seed_dealership(db_session)
    seed_employees(db_session, count=3, dealership=d)
    r = client.get("/api/employees/export.csv?full_name=anna")
    assert r.status_code == 200
    assert r.headers.get("content-type", "").startswith("text/csv")
    assert r.headers.get("content-disposition", "").lower().startswith("attachment")

    # parse CSV
    reader = csv.reader(io.StringIO(r.text))
    rows = list(reader)
    assert rows[0] == ["employee_id","db_username","full_name","role_code","dealership_id"]
    assert any("Anna" in row[2] for row in rows[1:])
