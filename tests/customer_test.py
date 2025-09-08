
import urllib.parse
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Importăm routerul real + simbolul get_db pe care îl vom suprascrie
from api.routes import customers as customers_module
# Importăm modelul și Base (DeclarativeBase) pentru a crea tabelele în DB de test
from models.customer import Base as CustomerBase, Customer


# -----------------------------
# FIXTURE DB & APP DE TEST
# -----------------------------
@pytest.fixture(scope="session")
def test_engine():
    """
    Folosește un SQLite in-memory partajat (StaticPool) ca să păstrăm aceeași conexiune
    pe toată durata testelor. E foarte rapid și complet izolat de Oracle.
    """
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    CustomerBase.metadata.create_all(bind=engine)
    yield engine
    CustomerBase.metadata.drop_all(bind=engine)



@pytest.fixture()
def db_session(test_engine):
    # o conexiune dedicată fiecărui test
    connection = test_engine.connect()
    # tranzacție părinte (va "îmbrăca" toate commit-urile din sesiune)
    trans = connection.begin()

    SessionLocal = sessionmaker(bind=connection, autoflush=False, autocommit=False, future=True)
    session = SessionLocal()

    # savepoint pentru a permite "commit"-uri în interior fără a închide tranzacția părinte
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans_):
        # când un savepoint se închide (ex: după un commit în endpoint), deschidem altul
        if trans_.nested and not trans_._parent.nested:
            sess.begin_nested()

    try:
        yield session
    finally:
        session.close()
        # anulăm TOT ce s-a făcut în test (inclusiv commit-urile din API)
        trans.rollback()
        connection.close()


@pytest.fixture()
def client(db_session):
    """
    Creează o aplicație FastAPI mică, doar cu routerul /customers,
    și suprascrie dependency-ul get_db cu db_session-ul nostru de test.
    """
    app = FastAPI()
    app.include_router(customers_module.router, prefix="/api")

    def override_get_db():
        # Important: folosim exact simbolul importat în modulul routerului
        # pentru a suprascrie dependency-ul corect.
        yield db_session

    app.dependency_overrides[customers_module.get_db] = override_get_db
    return TestClient(app)



# -----------------------------
# HELPER PENTRU SEED
# -----------------------------
def seed_customers(session, many: int = 3):
    """
    Populează rapid clienți de test.
    Notă: nu dăm commit; obiectele rămân vizibile în aceeași sesiune (și API folosește aceeași sesiune).
    """
    data = [
        Customer(full_name="Ioana Georgescu", phone="+40 721 111 222", email="ioana@example.com"),
        Customer(full_name="Radu Petrescu",   phone="+40 721 111 222", email="radu@example.com"),
        Customer(full_name="carmen dobre",    phone="+40 700 000 001", email="carmen@example.com"),
        Customer(full_name="Ionut Ionescu",   phone="+40 700 000 002", email="ionut@example.com"),
        Customer(full_name="IONA Pop",        phone="+40 733 333 333", email="iona@example.com"),
    ]
    rows = data[:many]
    session.add_all(rows)
    session.flush()  # ca să avem customer_id populate
    return rows


# -----------------------------
# TESTE CRUD BAZĂ
# -----------------------------
class TestCustomersAPI:
    def test_create_customer_success(self, client):
        payload = {"full_name": "Ana Maria", "phone": "+40 700 111 111", "email": "ana.maria@example.com"}
        r = client.post("/api/customers", json=payload)
        assert r.status_code == 201
        body = r.json()
        assert body["customer_id"] > 0
        assert body["full_name"] == payload["full_name"]
        assert body["phone"] == payload["phone"]
        assert body["email"] == payload["email"]

        # GET by id
        cid = body["customer_id"]
        g = client.get(f"/api/customers/{cid}")
        assert g.status_code == 200
        assert g.json()["customer_id"] == cid

    def test_create_customer_invalid_email_422(self, client):
        r = client.post("/api/customers", json={"full_name": "Bad Email", "email": "not-an-email"})
        assert r.status_code == 422  # EmailStr/email-validator respinge

    def test_create_customer_missing_full_name_422(self, client):
        r = client.post("/api/customers", json={"phone": "123"})
        assert r.status_code == 422  # full_name e obligatoriu

    def test_get_customer_not_found_404(self, client):
        r = client.get("/api/customers/999999")
        assert r.status_code == 404

    def test_update_customer_partial(self, client):
        # creăm
        r = client.post("/api/customers", json={"full_name": "Update Me", "phone": "1", "email": "up@example.com"})
        cid = r.json()["customer_id"]

        # actualizăm doar telefonul
        u = client.put(f"/api/customers/{cid}", json={"phone": "+40 755 555 555"})
        assert u.status_code == 200
        assert u.json()["phone"] == "+40 755 555 555"

    def test_delete_customer_then_404(self, client):
        r = client.post("/api/customers", json={"full_name": "Delete Me"})
        cid = r.json()["customer_id"]

        d = client.delete(f"/api/customers/{cid}")
        assert d.status_code == 204

        g = client.get(f"/api/customers/{cid}")
        assert g.status_code == 404


# -----------------------------
# TESTE LISTARE / SORT / FILTRARE / PAGINARE
# -----------------------------
def test_list_sort_asc_desc(client, db_session):
    rows = seed_customers(db_session, many=3)
    ids = [c.customer_id for c in rows]

    r1 = client.get("/api/customers?sort=asc")
    assert r1.status_code == 200
    returned_ids = [it["customer_id"] for it in r1.json()]
    # primele 3 ar trebui să fie în ordine crescătoare dacă lista e curată:
    assert returned_ids[:3] == sorted(ids)

    r2 = client.get("/api/customers?sort=desc")
    assert r2.status_code == 200
    returned_ids_desc = [it["customer_id"] for it in r2.json()]
    assert returned_ids_desc[:3] == sorted(ids, reverse=True)


def test_filter_full_name_like_case_insensitive(client, db_session):
    seed_customers(db_session, many=5)
    # căutăm "io" - să potrivească "Ioana", "IONA", "Ionut" (LIKE/ILIKE)
    r = client.get("/api/customers?full_name=io")
    assert r.status_code == 200
    names = [it["full_name"] for it in r.json()]
    assert any("Ioana" in n or "IONA" in n or "Ionut" in n for n in names)


def test_by_phone_exact_match(client, db_session):
    seed_customers(db_session, many=3)  # primele 2 au același telefon "+40 721 111 222"
    phone = urllib.parse.quote_plus("+40 721 111 222")
    r = client.get(f"/api/customers/by-phone/{phone}")
    assert r.status_code == 200
    body = r.json()
    # ar trebui să returneze 2 rezultate cu exact acest telefon
    assert len(body) >= 2
    assert all(it["phone"] == "+40 721 111 222" for it in body)


def test_by_email_exact_match_multiple(client, db_session):
    # creăm 2 clienți cu același email (schema NU are UNIQUE) -> API va returna ambele
    c1 = Customer(full_name="Dup1", email="dup@example.com")
    c2 = Customer(full_name="Dup2", email="dup@example.com")
    db_session.add_all([c1, c2])
    db_session.flush()

    email = urllib.parse.quote("dup@example.com", safe="")
    r = client.get(f"/api/customers/by-email/{email}")
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 2
    assert {b["full_name"] for b in body} == {"Dup1", "Dup2"}


def test_pagination_skip_limit(client, db_session):
    seed_customers(db_session, many=5)
    r = client.get("/api/customers?sort=asc&skip=2&limit=2")
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 2  # exact 2 rezultate


def test_invalid_sort_param_422(client):
    r = client.get("/api/customers?sort=sideways")
    assert r.status_code == 422  # regex-ul din Query cere asc|desc


def test_field_length_validation_422(client):
    # full_name > 120, phone > 40 => 422
    long_name = "x" * 121
    long_phone = "1" * 41
    r = client.post("/api/customers", json={"full_name": long_name, "phone": long_phone})
    assert r.status_code == 422


# -----------------------------
# TESTE EXPECTATE SĂ PICE (xfail)
# -----------------------------
@pytest.mark.xfail(reason="Schema nu are UNIQUE(email); API nu returnează 409 la email duplicat.")
def test_create_duplicate_email_should_conflict_409(client):
    payload = {"full_name": "A", "email": "dup1@example.com"}
    r1 = client.post("/api/customers", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/api/customers", json=payload)
    # Dorința (business rule): 409 Conflict; Realitatea curentă: 201 (acceptă duplicate)
    assert r2.status_code == 409


@pytest.mark.xfail(reason="Endpointul /by-phone face match exact, nu parțial.")
def test_by_phone_partial_match_should_work(client, db_session):
    seed_customers(db_session, many=3)
    # Căutăm doar prefixul; ne-am aștepta să găsească, dar endpointul cere egalitate
    r = client.get("/api/customers/by-phone/+40%20721")
    assert r.status_code == 200
    body = r.json()
    assert len(body) >= 1  # Va pica: acum întoarce 0


@pytest.mark.xfail(reason="Căutarea după email e case-sensitive în implementarea actuală.")
def test_by_email_case_insensitive_should_match(client, db_session):
    seed_customers(db_session, many=1)  # conține "ioana@example.com"
    r = client.get("/api/customers/by-email/IOANA%40EXAMPLE.COM")
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1  # Va pica: match-ul e exact, nu case-insensitive
