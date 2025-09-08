# owner:POP MIRCEA STEFAN
# CRATE_DATE: 2024-06-20 10:40
# LAST MODIFY_DATE: --
# MODIFY BY: --

#script care insreaza cate 3 valori pentru fiecare tabelă.

# ALTER SESSION SET CURRENT_SCHEMA=APP_OWNER;
#
# -------------------------------------------------------------------------------
# -- 1) DEALERSHIP (3)
# -------------------------------------------------------------------------------
# INSERT INTO dealership (name, city, region)
# VALUES ('Endava Auto București', 'București', 'Sud-Muntenia');
#
# INSERT INTO dealership (name, city, region)
# VALUES ('Endava Auto Cluj', 'Cluj-Napoca', 'Nord-Vest');
#
# INSERT INTO dealership (name, city, region)
# VALUES ('Endava Auto Iași', 'Iași', 'Nord-Est');
#
#
# -------------------------------------------------------------------------------
# -- 2) EMPLOYEE (3)  -> le legăm de dealership prin subselect pe nume
# -------------------------------------------------------------------------------
# INSERT INTO employee (db_username, full_name, role_code, dealership_id)
# VALUES (
#   'SALES_ANNA',
#   'Anna Ionescu',
#   'SALES',
#   (SELECT d.dealership_id FROM dealership d WHERE d.name = 'Endava Auto București')
# );
#
# INSERT INTO employee (db_username, full_name, role_code, dealership_id)
# VALUES (
#   'SALES_MIHNEA',
#   'Mihnea Pop',
#   'SALES',
#   (SELECT d.dealership_id FROM dealership d WHERE d.name = 'Endava Auto Cluj')
# );
#
# INSERT INTO employee (db_username, full_name, role_code, dealership_id)
# VALUES (
#   'MGR_BOB',
#   'Bob Marinescu',
#   'MANAGER',
#   (SELECT d.dealership_id FROM dealership d WHERE d.name = 'Endava Auto București')
# );
#
#
# -------------------------------------------------------------------------------
# -- 3) CUSTOMER (3)
# -------------------------------------------------------------------------------
# INSERT INTO customer (full_name, phone, email)
# VALUES ('Ioana Georgescu',  '+40 721 111 222', 'ioana.georgescu@example.com');
#
# INSERT INTO customer (full_name, phone, email)
# VALUES ('Radu Petrescu',    '+40 722 333 444', 'radu.petrescu@example.com');
#
# INSERT INTO customer (full_name, phone, email)
# VALUES ('Carmen Dobre',     '+40 723 555 666', 'carmen.dobre@example.com');
#
#
# -------------------------------------------------------------------------------
# -- 4) VEHICLE (3)  -> VIN unice, model, an, preț de bază
# -------------------------------------------------------------------------------
# INSERT INTO vehicle (vin, model, trim_level, model_year, base_price)
# VALUES ('WVWZZZ1JZXA000001', 'Golf',   'Highline', 2024, 22000);
#
# INSERT INTO vehicle (vin, model, trim_level, model_year, base_price)
# VALUES ('WVGZZZ5NZYA000002', 'Tiguan', 'R-Line',   2025, 36000);
#
# INSERT INTO vehicle (vin, model, trim_level, model_year, base_price)
# VALUES ('WV1ZZZ2HZBA000003', 'Passat', 'Elegance', 2023, 30000);
#
#
# -------------------------------------------------------------------------------
# -- 5) SERVICE_ITEM (3)
# -------------------------------------------------------------------------------
# INSERT INTO service_item (service_type, name, description, list_price)
# VALUES ('EXTRA_OPTION', 'Pachet Tech', 'Navigație, cockpit digital, senzori parcare', 1500);
#
# INSERT INTO service_item (service_type, name, description, list_price)
# VALUES ('CASCO', 'CASCO 12 luni', 'Asigurare completă pe 12 luni', 900);
#
# INSERT INTO service_item (service_type, name, description, list_price)
# VALUES ('EXTENDED_WARRANTY', 'Garanție extinsă 2 ani', 'Extindere garanție producător', 1200);
#
#
# -------------------------------------------------------------------------------
# -- 6) SALE_ORDER (3)  -> legăm prin subselect: dealership (după nume), client (după email),
# --                        salesperson/manager (după db_username). created_by = username app.
# -- Notă: total_amount îl lăsăm NULL inițial; se va calcula după inserarea liniilor.
# -------------------------------------------------------------------------------
# -- Comandă #1 (client Ioana, București, vânzător Anna, cu manager Bob)
# INSERT INTO sale_order (
#   dealership_id, customer_id, salesperson_id, manager_id,
#   order_date, status, total_amount, created_by
# )
# VALUES (
#   (SELECT dealership_id FROM dealership WHERE name = 'Endava Auto București'),
#   (SELECT customer_id   FROM customer   WHERE email = 'ioana.georgescu@example.com'),
#   (SELECT employee_id   FROM employee   WHERE db_username = 'SALES_ANNA'),
#   (SELECT employee_id   FROM employee   WHERE db_username = 'MGR_BOB'),
#   DATE '2025-09-01',
#   'OPEN',
#   NULL,
#   'SALES_ANNA'
# );
#
# -- Comandă #2 (client Radu, Cluj, vânzător Mihnea, fără manager)
# INSERT INTO sale_order (
#   dealership_id, customer_id, salesperson_id, manager_id,
#   order_date, status, total_amount, created_by
# )
# VALUES (
#   (SELECT dealership_id FROM dealership WHERE name = 'Endava Auto Cluj'),
#   (SELECT customer_id   FROM customer   WHERE email = 'radu.petrescu@example.com'),
#   (SELECT employee_id   FROM employee   WHERE db_username = 'SALES_MIHNEA'),
#   NULL,
#   DATE '2025-09-02',
#   'OPEN',
#   NULL,
#   'SALES_MIHNEA'
# );
#
# -- Comandă #3 (client Carmen, București, vânzător Anna, fără manager)
# INSERT INTO sale_order (
#   dealership_id, customer_id, salesperson_id, manager_id,
#   order_date, status, total_amount, created_by
# )
# VALUES (
#   (SELECT dealership_id FROM dealership WHERE name = 'Endava Auto București'),
#   (SELECT customer_id   FROM customer   WHERE email = 'carmen.dobre@example.com'),
#   (SELECT employee_id   FROM employee   WHERE db_username = 'SALES_ANNA'),
#   NULL,
#   DATE '2025-09-03',
#   'OPEN',
#   NULL,
#   'SALES_ANNA'
# );
#
#
# -------------------------------------------------------------------------------
# -- 7) SALE_ITEM (3)  -> câte un item per comandă (2 mașini + 1 serviciu).
# -- unit_price e preluat din vehicle.base_price / service_item.list_price.
# -------------------------------------------------------------------------------
# -- Item pt Comanda #1: CAR = Golf
# INSERT INTO sale_item (order_id, item_type, vehicle_id, service_id, qty, unit_price)
# VALUES (
#   (SELECT so.order_id
#      FROM sale_order so
#      JOIN customer c ON c.customer_id = so.customer_id
#     WHERE c.email = 'ioana.georgescu@example.com'
#       AND so.order_date = DATE '2025-09-01'),
#   'CAR',
#   (SELECT v.vehicle_id FROM vehicle v WHERE v.vin = 'WVWZZZ1JZXA000001'),
#   NULL,
#   1,
#   (SELECT v.base_price FROM vehicle v WHERE v.vin = 'WVWZZZ1JZXA000001')
# );
#
# -- Item pt Comanda #2: SERVICE = CASCO 12 luni
# INSERT INTO sale_item (order_id, item_type, vehicle_id, service_id, qty, unit_price)
# VALUES (
#   (SELECT so.order_id
#      FROM sale_order so
#      JOIN customer c ON c.customer_id = so.customer_id
#     WHERE c.email = 'radu.petrescu@example.com'
#       AND so.order_date = DATE '2025-09-02'),
#   'SERVICE',
#   NULL,
#   (SELECT s.service_id FROM service_item s WHERE s.name = 'CASCO 12 luni'),
#   1,
#   (SELECT s.list_price FROM service_item s WHERE s.name = 'CASCO 12 luni')
# );
#
# -- Item pt Comanda #3: CAR = Tiguan
# INSERT INTO sale_item (order_id, item_type, vehicle_id, service_id, qty, unit_price)
# VALUES (
#   (SELECT so.order_id
#      FROM sale_order so
#      JOIN customer c ON c.customer_id = so.customer_id
#     WHERE c.email = 'carmen.dobre@example.com'
#       AND so.order_date = DATE '2025-09-03'),
#   'CAR',
#   (SELECT v.vehicle_id FROM vehicle v WHERE v.vin = 'WVGZZZ5NZYA000002'),
#   NULL,
#   1,
#   (SELECT v.base_price FROM vehicle v WHERE v.vin = 'WVGZZZ5NZYA000002')
# );
#
# -------------------------------------------------------------------------------
# -- (Opțional) Dacă vrei să setezi total_amount după ce ai introdus liniile:
# -- Actualizăm total_amount ca SUM(line_total) pentru fiecare comandă.
# -------------------------------------------------------------------------------
# -- UPDATE sale_order so
# -- SET so.total_amount = (
# --   SELECT SUM(si.line_total)
# --   FROM sale_item si
# --   WHERE si.order_id = so.order_id
# -- );
# -- COMMIT;


import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1) Importă aplicația (după ce o să patch-uim engine-ul)
from main import app
import database.engine as db_engine_mod   # modulul de engine al app-ului
from database.engine import Base
from database.session import get_db
from core.config import settings

# 2) Importă modelele pentru metadata (IMPORTANT!)
#    dacă nu imporți modelele, Base.metadata nu știe de tabele și create_all() nu le creează.
from models.dealership import Dealership  # noqa: F401


# owner:POP MIRCEA STEFAN
# CRATE_DATE: 2024-06-20 10:40
# LAST MODIFY_DATE: --
# MODIFY BY: --

#script care insreaza cate 3 valori pentru fiecare tabelă.

# ALTER SESSION SET CURRENT_SCHEMA=APP_OWNER;
#
# -------------------------------------------------------------------------------
# -- 1) DEALERSHIP (3)
# -------------------------------------------------------------------------------
# INSERT INTO dealership (name, city, region)
# VALUES ('Endava Auto București', 'București', 'Sud-Muntenia');
#
# INSERT INTO dealership (name, city, region)
# VALUES ('Endava Auto Cluj', 'Cluj-Napoca', 'Nord-Vest');
#
# INSERT INTO dealership (name, city, region)
# VALUES ('Endava Auto Iași', 'Iași', 'Nord-Est');
#
#
# -------------------------------------------------------------------------------
# -- 2) EMPLOYEE (3)  -> le legăm de dealership prin subselect pe nume
# -------------------------------------------------------------------------------
# INSERT INTO employee (db_username, full_name, role_code, dealership_id)
# VALUES (
#   'SALES_ANNA',
#   'Anna Ionescu',
#   'SALES',
#   (SELECT d.dealership_id FROM dealership d WHERE d.name = 'Endava Auto București')
# );
#
# INSERT INTO employee (db_username, full_name, role_code, dealership_id)
# VALUES (
#   'SALES_MIHNEA',
#   'Mihnea Pop',
#   'SALES',
#   (SELECT d.dealership_id FROM dealership d WHERE d.name = 'Endava Auto Cluj')
# );
#
# INSERT INTO employee (db_username, full_name, role_code, dealership_id)
# VALUES (
#   'MGR_BOB',
#   'Bob Marinescu',
#   'MANAGER',
#   (SELECT d.dealership_id FROM dealership d WHERE d.name = 'Endava Auto București')
# );
#
#
# -------------------------------------------------------------------------------
# -- 3) CUSTOMER (3)
# -------------------------------------------------------------------------------
# INSERT INTO customer (full_name, phone, email)
# VALUES ('Ioana Georgescu',  '+40 721 111 222', 'ioana.georgescu@example.com');
#
# INSERT INTO customer (full_name, phone, email)
# VALUES ('Radu Petrescu',    '+40 722 333 444', 'radu.petrescu@example.com');
#
# INSERT INTO customer (full_name, phone, email)
# VALUES ('Carmen Dobre',     '+40 723 555 666', 'carmen.dobre@example.com');
#
#
# -------------------------------------------------------------------------------
# -- 4) VEHICLE (3)  -> VIN unice, model, an, preț de bază
# -------------------------------------------------------------------------------
# INSERT INTO vehicle (vin, model, trim_level, model_year, base_price)
# VALUES ('WVWZZZ1JZXA000001', 'Golf',   'Highline', 2024, 22000);
#
# INSERT INTO vehicle (vin, model, trim_level, model_year, base_price)
# VALUES ('WVGZZZ5NZYA000002', 'Tiguan', 'R-Line',   2025, 36000);
#
# INSERT INTO vehicle (vin, model, trim_level, model_year, base_price)
# VALUES ('WV1ZZZ2HZBA000003', 'Passat', 'Elegance', 2023, 30000);
#
#
# -------------------------------------------------------------------------------
# -- 5) SERVICE_ITEM (3)
# -------------------------------------------------------------------------------
# INSERT INTO service_item (service_type, name, description, list_price)
# VALUES ('EXTRA_OPTION', 'Pachet Tech', 'Navigație, cockpit digital, senzori parcare', 1500);
#
# INSERT INTO service_item (service_type, name, description, list_price)
# VALUES ('CASCO', 'CASCO 12 luni', 'Asigurare completă pe 12 luni', 900);
#
# INSERT INTO service_item (service_type, name, description, list_price)
# VALUES ('EXTENDED_WARRANTY', 'Garanție extinsă 2 ani', 'Extindere garanție producător', 1200);
#
#
# -------------------------------------------------------------------------------
# -- 6) SALE_ORDER (3)  -> legăm prin subselect: dealership (după nume), client (după email),
# --                        salesperson/manager (după db_username). created_by = username app.
# -- Notă: total_amount îl lăsăm NULL inițial; se va calcula după inserarea liniilor.
# -------------------------------------------------------------------------------
# -- Comandă #1 (client Ioana, București, vânzător Anna, cu manager Bob)
# INSERT INTO sale_order (
#   dealership_id, customer_id, salesperson_id, manager_id,
#   order_date, status, total_amount, created_by
# )
# VALUES (
#   (SELECT dealership_id FROM dealership WHERE name = 'Endava Auto București'),
#   (SELECT customer_id   FROM customer   WHERE email = 'ioana.georgescu@example.com'),
#   (SELECT employee_id   FROM employee   WHERE db_username = 'SALES_ANNA'),
#   (SELECT employee_id   FROM employee   WHERE db_username = 'MGR_BOB'),
#   DATE '2025-09-01',
#   'OPEN',
#   NULL,
#   'SALES_ANNA'
# );
#
# -- Comandă #2 (client Radu, Cluj, vânzător Mihnea, fără manager)
# INSERT INTO sale_order (
#   dealership_id, customer_id, salesperson_id, manager_id,
#   order_date, status, total_amount, created_by
# )
# VALUES (
#   (SELECT dealership_id FROM dealership WHERE name = 'Endava Auto Cluj'),
#   (SELECT customer_id   FROM customer   WHERE email = 'radu.petrescu@example.com'),
#   (SELECT employee_id   FROM employee   WHERE db_username = 'SALES_MIHNEA'),
#   NULL,
#   DATE '2025-09-02',
#   'OPEN',
#   NULL,
#   'SALES_MIHNEA'
# );
#
# -- Comandă #3 (client Carmen, București, vânzător Anna, fără manager)
# INSERT INTO sale_order (
#   dealership_id, customer_id, salesperson_id, manager_id,
#   order_date, status, total_amount, created_by
# )
# VALUES (
#   (SELECT dealership_id FROM dealership WHERE name = 'Endava Auto București'),
#   (SELECT customer_id   FROM customer   WHERE email = 'carmen.dobre@example.com'),
#   (SELECT employee_id   FROM employee   WHERE db_username = 'SALES_ANNA'),
#   NULL,
#   DATE '2025-09-03',
#   'OPEN',
#   NULL,
#   'SALES_ANNA'
# );
#
#
# -------------------------------------------------------------------------------
# -- 7) SALE_ITEM (3)  -> câte un item per comandă (2 mașini + 1 serviciu).
# -- unit_price e preluat din vehicle.base_price / service_item.list_price.
# -------------------------------------------------------------------------------
# -- Item pt Comanda #1: CAR = Golf
# INSERT INTO sale_item (order_id, item_type, vehicle_id, service_id, qty, unit_price)
# VALUES (
#   (SELECT so.order_id
#      FROM sale_order so
#      JOIN customer c ON c.customer_id = so.customer_id
#     WHERE c.email = 'ioana.georgescu@example.com'
#       AND so.order_date = DATE '2025-09-01'),
#   'CAR',
#   (SELECT v.vehicle_id FROM vehicle v WHERE v.vin = 'WVWZZZ1JZXA000001'),
#   NULL,
#   1,
#   (SELECT v.base_price FROM vehicle v WHERE v.vin = 'WVWZZZ1JZXA000001')
# );
#
# -- Item pt Comanda #2: SERVICE = CASCO 12 luni
# INSERT INTO sale_item (order_id, item_type, vehicle_id, service_id, qty, unit_price)
# VALUES (
#   (SELECT so.order_id
#      FROM sale_order so
#      JOIN customer c ON c.customer_id = so.customer_id
#     WHERE c.email = 'radu.petrescu@example.com'
#       AND so.order_date = DATE '2025-09-02'),
#   'SERVICE',
#   NULL,
#   (SELECT s.service_id FROM service_item s WHERE s.name = 'CASCO 12 luni'),
#   1,
#   (SELECT s.list_price FROM service_item s WHERE s.name = 'CASCO 12 luni')
# );
#
# -- Item pt Comanda #3: CAR = Tiguan
# INSERT INTO sale_item (order_id, item_type, vehicle_id, service_id, qty, unit_price)
# VALUES (
#   (SELECT so.order_id
#      FROM sale_order so
#      JOIN customer c ON c.customer_id = so.customer_id
#     WHERE c.email = 'carmen.dobre@example.com'
#       AND so.order_date = DATE '2025-09-03'),
#   'CAR',
#   (SELECT v.vehicle_id FROM vehicle v WHERE v.vin = 'WVGZZZ5NZYA000002'),
#   NULL,
#   1,
#   (SELECT v.base_price FROM vehicle v WHERE v.vin = 'WVGZZZ5NZYA000002')
# );
#
# -------------------------------------------------------------------------------
# -- (Opțional) Dacă vrei să setezi total_amount după ce ai introdus liniile:
# -- Actualizăm total_amount ca SUM(line_total) pentru fiecare comandă.
# -------------------------------------------------------------------------------
# -- UPDATE sale_order so
# -- SET so.total_amount = (
# --   SELECT SUM(si.line_total)
# --   FROM sale_item si
# --   WHERE si.order_id = so.order_id
# -- );
# -- COMMIT;


import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1) Importă aplicația (după ce o să patch-uim engine-ul)
from main import app
import database.engine as db_engine_mod   # modulul de engine al app-ului
from database.engine import Base
from database.session import get_db
from core.config import settings

# 2) Importă modelele pentru metadata (IMPORTANT!)
#    dacă nu imporți modelele, Base.metadata nu știe de tabele și create_all() nu le creează.
from models.dealership import Dealership  # noqa: F401


# ------------------------------------------------------------------------------
# CONFIG: engine de test (SQLite pe disc, nu in-memory)
# Motiv: SQLite in-memory creează o DB pe fiecare conexiune; cum FastAPI + SQLAlchemy
# folosesc mai multe conexiuni, schema “dispare”. Un fișier local e stabil.
# ------------------------------------------------------------------------------
TEST_DB_PATH = "./test_dealership.db"
TEST_DB_URL = f"sqlite:///{TEST_DB_PATH}"

TEST_ENGINE = create_engine(
    TEST_DB_URL,
    future=True,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    bind=TEST_ENGINE,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


@pytest.fixture(scope="session", autouse=True)
def _patch_engine_and_prepare_schema():
    """
    1) Patch-uim engine-ul global folosit de aplicație cu TEST_ENGINE,
       atât în database.engine, cât și în main (care l-a importat by-value).
    2) Creăm schema o dată pe toată sesiunea de teste.
    """
    # 1. Redirecționează engine-ul din modulul database.engine
    db_engine_mod.engine = TEST_ENGINE

    # 2. Redirecționează engine-ul *și* în modulul main (importat de noi mai sus)
    #    ca on_startup() să creeze tabelele pe SQLite-ul nostru.
    import main as main_mod
    main_mod.engine = TEST_ENGINE

    # 3. Creează schema la începutul suite-ului
    Base.metadata.create_all(bind=TEST_ENGINE)

    yield

    # 4. Curăță după suite
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
    Creează un TestClient DUPĂ ce am patch-uit engine-ul și override la get_db.
    Folosim scope=function ca fiecare test să plece cu aplicația gata de folosit.
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
    # seed extra records
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
    # trebuie să conțină măcar o linie de date
    assert len(text.strip().splitlines()) >= 1