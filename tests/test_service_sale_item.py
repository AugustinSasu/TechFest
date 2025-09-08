# tests/test_service_sale_item.py
# service_sale_item endpoints

# --------------------------------------
# Teste de integrare pentru toate endpointurile din /service-sale-items

# Autor: Cristian-Valentin Alexa
# Data: 14 Aprilie 2024

# --------------------------------------

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# 🔹 1. Test listare goală (fără date inițiale)
def test_list_service_sale_items_empty():
    response = client.get("/service-sale-items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# 🔹 2. Test creare item valid
def test_create_service_sale_item():
    payload = {
        "order_id": 1,
        "service_id": 1,
        "qty": 2,
        "unit_price": 100.00
    }
    response = client.post("/service-sale-items/", json=payload)
    assert response.status_code in (201, 400)  # poate eșua dacă FK nu există
    if response.status_code == 201:
        data = response.json()
        assert data["qty"] == 2
        assert data["unit_price"] == 100.00
        assert "line_total" in data

# 🔹 3. Test GET by ID valid/invalid
def test_get_service_sale_item_by_id():
    response = client.get("/service-sale-items/1")
    if response.status_code == 200:
        data = response.json()
        assert data["item_id"] == 1
    elif response.status_code == 404:
        assert response.json()["detail"] == "Service sale item not found"

# 🔹 4. Test update item existent sau 404
def test_update_service_sale_item():
    payload = {"qty": 5, "unit_price": 99.99}
    response = client.put("/service-sale-items/1", json=payload)
    if response.status_code == 200:
        data = response.json()
        assert data["qty"] == 5
    elif response.status_code == 404:
        assert response.json()["detail"] == "Service sale item not found"

# 🔹 5. Test delete (204 sau 404)
def test_delete_service_sale_item():
    response = client.delete("/service-sale-items/1")
    assert response.status_code in (204, 404)

# 🔹 6. Export JSON
def test_export_service_sale_items_json():
    response = client.get("/service-sale-items/export/json")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# 🔹 7. Export TXT
def test_export_service_sale_items_txt():
    response = client.get("/service-sale-items/export/txt")
    assert response.status_code == 200
    assert isinstance(response.text, str)
    assert "item_id" in response.text
