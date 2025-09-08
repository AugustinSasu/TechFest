# -*- coding: utf-8 -*-
# owner: POP MIRCEA STEFAN
# create_date: 2024-06-20 10:40
# updated_for_tests: now

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

# 1) Aplicația + infrastructura DB a aplicației
from main import app
import database.engine as db_engine_mod
from database.engine import Base
from database.session import get_db
from core.config import settings

# 2) IMPORTĂ TOATE MODELELE ÎNAINTE DE create_all()
#    Ca Base.metadata să “știe” de toate tabelele și FK-urile.
from models.dealership import Dealership            # noqa: F401
from models.employee import Employee                # noqa: F401
from models.customer import Customer                # noqa: F401
from models.vehicle import Vehicle                  # noqa: F401
from models.service_item import ServiceItem         # noqa: F401
from models.sale_order import SaleOrder             # noqa: F401

# Unele proiecte au un singur tabel de linii (sale_item), altele două (car_/service_).
# Importă ce există, ignoră ce nu găsești.
try:
    from models.sale_item import SaleItem          # noqa: F401
except Exception:
    pass

try:
    from models.car_sale_item import CarSaleItem   # noqa: F401
    from models.service_sale_item import ServiceSaleItem  # noqa: F401
except Exception:
    pass


# ------------------------------------------------------------------------------
# CONFIG: engine de test (SQLite pe disc, NU in-memory – stabil pe mai multe conexiuni)
# ------------------------------------------------------------------------------
TEST_DB_PATH = "./test_dealership.db"
TEST_DB_URL = f"sqlite:///{TEST_DB_PATH}"

TEST_ENGINE = create_engine(
    TEST_DB_URL,
    future=True,
    connect_args={"check_same_thread": False},
)

# Activează foreign_keys în SQLite (pentru ON DELETE CASCADE etc.)
@event.listens_for(TEST_ENGINE, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cur = dbapi_connection.cursor()
    cur.execute("PRAGMA foreign_keys=ON")
    cur.close()

TestingSessionLocal = sessionmaker(
    bind=TEST_ENGINE,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)


@pytest.fixture(scope="session", autouse=True)
def _patch_engine_and_prepare_schema():
    """
    1) Înlocuiește engine-ul app-ului cu TEST_ENGINE (și în database.engine, și în main).
    2) Creează schema o singură dată pentru toată sesiunea de teste.
    3) Curăță la final.
    """
    # 1. Patch engine în modulul de infrastructură
    db_engine_mod.engine = TEST_ENGINE

    # 2. Patch engine și în modulul main (importat deja)
    import main as main_mod
    main_mod.engine = TEST_ENGINE

    # 3. Creează schema DUPĂ ce TOATE modelele au fost importate (vezi importurile de sus)
    Base.metadata.create_all(bind=TEST_ENGINE)

    yield

    # 4. Curățenie
    Base.metadata.drop_all(bind=TEST_ENGINE)
    try:
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
    except Exception:
        pass


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    """
    Creează un TestClient cu override la get_db pentru fiecare test.
    """
    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


API = f"{settings.API_V1_PREFIX}/dealerships"


# ------------------------------------------------------------------------------
# TESTE
# ------------------------------------------------------------------------------
def test_healthcheck_ok(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_create_and_get_dealership(client: TestClient):
    payload = {"name": "VW Center", "city": "Cluj", "region": "Transilvania"}
    r = client.post(API, json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["name"] == "VW Center"
    assert data["city"] == "Cluj"
    assert "dealership_id" in data

    did = data["dealership_id"]
    r2 = client.get(f"{API}/{did}")
    assert r2.status_code == 200
    assert r2.json()["name"] == "VW Center"


def test_list_sort_and_filters(client: TestClient):
    # seed extra records (pot exista deja din testul anterior, nu contăm pe ordinea globală)
    client.post(API, json={"name": "Audi Shop", "city": "Cluj", "region": "Transilvania"})
    client.post(API, json={"name": "Skoda House", "city": "Bucuresti", "region": "Muntenia"})
    client.post(API, json={"name": "Seat Market", "city": "Cluj", "region": "Transilvania"})

    # sort asc (alfabetic)
    r = client.get(API, params={"sort": "asc"})
    assert r.status_code == 200
    names = [x["name"] for x in r.json()]
    assert names == sorted(names)

    # sort desc (alfabetic invers)
    r = client.get(API, params={"sort": "desc"})
    assert r.status_code == 200
    names_desc = [x["name"] for x in r.json()]
    assert names_desc == sorted(names_desc, reverse=True)

    # filter by q (substring în nume, case-insensitive)
    r = client.get(API, params={"q": "Shop"})
    assert r.status_code == 200
    res = r.json()
    assert len(res) >= 1
    assert all("shop" in x["name"].lower() for x in res)

    # filter by city
    r = client.get(API, params={"city": "Cluj"})
    assert r.status_code == 200
    assert all(x["city"] == "Cluj" for x in r.json())

    # filter by region
    r = client.get(API, params={"region": "Muntenia"})
    assert r.status_code == 200
    assert all(x["region"] == "Muntenia" for x in r.json())


def test_update_and_delete(client: TestClient):
    # create one
    r = client.post(API, json={"name": "Temp Dealer", "city": "Iasi", "region": "Moldova"})
    assert r.status_code == 201
    did = r.json()["dealership_id"]

    # update (parțial)
    r2 = client.put(f"{API}/{did}", json={"city": "Iasi-Nou"})
    assert r2.status_code == 200
    assert r2.json()["city"] == "Iasi-Nou"

    # delete
    r3 = client.delete(f"{API}/{did}")
    assert r3.status_code == 204

    # 404 după ștergere
    r4 = client.get(f"{API}/{did}")
    assert r4.status_code == 404


def test_exports_json_and_txt(client: TestClient):
    rj = client.get(f"{API}/_export/json")
    assert rj.status_code == 200
    data = rj.json()
    assert isinstance(data, list)
    if data:
        assert {"dealership_id", "name", "city", "region"} <= set(data[0].keys())

    rt = client.get(f"{API}/_export/txt")
    assert rt.status_code == 200
    text = rt.text
    assert "dealership_id | name | city | region" in text
    # trebuie să conțină antet + cel puțin o linie de date (dacă există în DB)
    assert len([ln for ln in text.strip().splitlines() if ln.strip()]) >= 1
