# tests/test_vehicle.py
# vehicles endpoints

# -----------------------------
# Teste complete pentru entitatea vehicle: CRUD + filtre + exporturi

# Autor: Cristian-Valentin Alexa
# Data: 14 Aprilie 2024

# -----------------------------

from fastapi.testclient import TestClient


import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app

client = TestClient(app)

# 🔹 1. Test listare inițială (goală sau populată)
def test_list_vehicles():
    response = client.get("/vehicles")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# 🔹 2. Test creare vehicul valid
def test_create_vehicle():
    payload = {
        "vin": "TESTVIN0001",
        "model": "Golf",
        "trim_level": "Comfortline",
        "model_year": 2024,
        "base_price": 18500.0
    }
    response = client.post("/vehicles", json=payload)
    assert response.status_code in (201, 400)  # poate da 400 dacă vin e duplicat
    if response.status_code == 201:
        data = response.json()
        assert data["vin"] == "TESTVIN0001"
        assert data["model"] == "Golf"

# 🔹 3. Test get by ID valid/invalid
def test_get_vehicle_by_id():
    response = client.get("/vehicles/1")
    if response.status_code == 200:
        data = response.json()
        assert "vehicle_id" in data
    elif response.status_code == 404:
        assert response.json()["detail"] == "Vehicle not found"

# 🔹 4. Update vehicul existent
def test_update_vehicle():
    payload = {"model": "Golf GTI"}
    response = client.put("/vehicles/1", json=payload)
    if response.status_code == 200:
        assert response.json()["model"] == "Golf GTI"
    elif response.status_code == 404:
        assert response.json()["detail"] == "Vehicle not found"

# 🔹 5. Delete vehicul
def test_delete_vehicle():
    response = client.delete("/vehicles/1")
    assert response.status_code in (204, 404)

# 🔹 6. Export JSON
def test_export_vehicles_json():
    response = client.get("/vehicles/export/json")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# 🔹 7. Export TXT
def test_export_vehicles_txt():
    response = client.get("/vehicles/export/txt")
    assert response.status_code == 200
    assert "vehicle_id" in response.text
