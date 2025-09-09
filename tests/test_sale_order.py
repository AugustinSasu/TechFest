# 📁 tests/test_sale_order.py
# ✅ TESTE: /sale-orders endpoints
# --------------------------------
# Teste de integrare pentru entitatea `sale_order` (comandă vânzare auto)


# Autor: Alexa Cristian-Valentin
# Data: 09.09.2024

from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app

client = TestClient(app)

# 🔹 1. Listare inițială (fără date)
def test_list_sale_orders_empty():
    response = client.get("/api/v1/sale-orders")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# 🔹 2. Creare comandă validă (doar dacă FK-urile există)
def test_create_sale_order():
    payload = {
        "dealership_id": 1,
        "customer_id": 1,
        "salesperson_id": 1,
        "manager_id": 1,
        "status": "OPEN",
        "total_amount": 25000.0,
        "created_by": "SALES_ANNA"
    }
    response = client.post("/api/v1/sale-orders", json=payload)
    assert response.status_code in (201, 400)
    if response.status_code == 201:
        data = response.json()
        assert data["status"] == "OPEN"
        assert "order_id" in data

# 🔹 3. GET by ID valid/invalid
def test_get_sale_order():
    response = client.get("/api/v1/sale-orders/1")
    if response.status_code == 200:
        assert "order_id" in response.json()
    elif response.status_code == 404:
        assert response.json()["detail"] == "Sale order not found"

# 🔹 4. UPDATE status sau total_amount
def test_update_sale_order():
    payload = {"status": "APPROVED", "total_amount": 27500.00}
    response = client.put("/api/v1/sale-orders/1", json=payload)
    if response.status_code == 200:
        assert response.json()["status"] == "APPROVED"
    elif response.status_code == 404:
        assert response.json()["detail"] == "Sale order not found"

# 🔹 5. Ștergere comandă
def test_delete_sale_order():
    response = client.delete("/api/v1/sale-orders/1")
    assert response.status_code in (204, 404)
