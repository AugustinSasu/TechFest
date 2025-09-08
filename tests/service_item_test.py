# tests/service_item_test.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_service_item():
    payload = {
        "service_type": "CASCO",
        "name": "Full CASCO Plus",
        "description": "Acoperire completă",
        "list_price": 800.00
    }
    r = client.post("/api/v1/service-items/", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["service_type"] == "CASCO"
    assert data["name"] == "Full CASCO Plus"
    assert float(data["list_price"]) == 800.00

def test_list_service_items():
    r = client.get("/api/v1/service-items/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
