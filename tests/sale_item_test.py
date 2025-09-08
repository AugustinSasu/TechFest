# tests/sale_item_test.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_sale_item_car():
    payload = {
        "order_id": 1,
        "item_type": "CAR",
        "vehicle_id": 1,
        "qty": 1,
        "unit_price": 20000
    }
    r = client.post("/api/v1/sale-items/", json=payload)
    if r.status_code == 400:
        assert r.json()["detail"] == "CAR items require vehicle_id"
    else:
        assert r.status_code == 201
        data = r.json()
        assert data["item_type"] == "CAR"
        assert data["line_total"] == 20000

def test_create_sale_item_service():
    payload = {
        "order_id": 1,
        "item_type": "SERVICE",
        "service_id": 1,
        "qty": 2,
        "unit_price": 100
    }
    r = client.post("/api/v1/sale-items/", json=payload)
    if r.status_code == 400:
        assert r.json()["detail"] == "SERVICE items require service_id"
    else:
        assert r.status_code == 201
        data = r.json()
        assert data["item_type"] == "SERVICE"
        assert data["line_total"] == 200
