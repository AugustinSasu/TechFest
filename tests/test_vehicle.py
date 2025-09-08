# tests/vehicle_test.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_vehicle():
    payload = {
        "vin": "TESTVIN1234567890",
        "model": "Golf",
        "trim_level": "Comfortline",
        "model_year": 2022,
        "base_price": 19500.00
    }
    response = client.post("/api/v1/vehicles/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["model"] == "Golf"
    assert data["vin"] == "TESTVIN1234567890"
    assert data["base_price"] == 19500.00

def test_get_vehicle_list():
    response = client.get("/api/v1/vehicles/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_filter_vehicle_by_year():
    response = client.get("/api/v1/vehicles/?model_year=2022")
    assert response.status_code == 200
    data = response.json()
    for item in data:
        assert item["model_year"] == 2022
