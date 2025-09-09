import pytest
from fastapi.testclient import TestClient

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app

client = TestClient(app)

def create_sample_item():
    payload = {
        "service_type": "EXTRA_OPTION",
        "name": "Test Service",
        "description": "Test desc",
        "list_price": 123.45
    }
    r = client.post("/api/service-items/", json=payload)
    assert r.status_code == 201
    return r.json()

def test_create_service_item():
    payload = {
        "service_type": "CASCO",
        "name": "Full CASCO Plus",
        "description": "Acoperire completă",
        "list_price": 800.00
    }
    r = client.post("/api/service-items/", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["service_type"] == "CASCO"
    assert data["name"] == "Full CASCO Plus"
    assert float(data["list_price"]) == 800.00

def test_create_service_item_missing_required():
    payload = {
        "name": "No Type"
    }
    r = client.post("/api/service-items/", json=payload)
    assert r.status_code == 422

def test_list_service_items():
    r = client.get("/api/service-items/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_list_service_items_with_query():
    create_sample_item()
    r = client.get("/api/service-items/?q=Test")
    assert r.status_code == 200
    items = r.json()
    assert any("Test Service" in i["name"] for i in items)

def test_get_service_item():
    item = create_sample_item()
    r = client.get(f"/api/service-items/{item['service_id']}")
    assert r.status_code == 200
    data = r.json()
    assert data["service_id"] == item["service_id"]

def test_get_service_item_not_found():
    r = client.get("/api/service-items/999999")
    assert r.status_code == 404

def test_update_service_item():
    item = create_sample_item()
    payload = {"name": "Updated Name"}
    r = client.put(f"/api/service-items/{item['service_id']}", json=payload)
    assert r.status_code == 200
    assert r.json()["name"] == "Updated Name"

def test_update_service_item_not_found():
    payload = {"name": "Doesn't matter"}
    r = client.put("/api/service-items/999999", json=payload)
    assert r.status_code == 404

def test_delete_service_item():
    item = create_sample_item()
    r = client.delete(f"/api/service-items/{item['service_id']}")
    assert r.status_code == 204
    # Confirm deletion
    r2 = client.get(f"/api/service-items/{item['service_id']}")
    assert r2.status_code == 404

def test_delete_service_item_not_found():
    r = client.delete("/api/service-items/999999")
    assert r.status_code == 404

def test_export_service_items_json():
    r = client.get("/api/service-items/export/json")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_export_service_items_txt():
    r = client.get("/api/service-items/export/txt")
    assert r.status_code == 200
    assert isinstance(r.text, str)
    assert "service_id" in r.text