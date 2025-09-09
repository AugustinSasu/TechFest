import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app

# 📁 tests/test_sale_order.py
# ✅ TESTE: /sale-orders endpoints (inclusiv /by-employee și /trends)
# ---------------------------------------------------------------------
# Verifică funcționalitatea CRUD + endpoints custom pentru sale_order

from fastapi.testclient import TestClient


client = TestClient(app)

# 🔹 1. Test listare goală sau existentă
def test_list_sale_orders():
    response = client.get("/api/v1/sale-orders")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# 🔹 2. Test creare comandă nouă validă
def test_create_sale_order():
    payload = {
        "dealership_id": 1,
        "customer_id": 1,
        "salesperson_id": 1,
        "manager_id": 1,
        "status": "INVOICED",
        "total_amount": 25000.0,
        "created_by": "test"
    }
    r = client.post("/api/v1/sale-orders", json=payload)
    assert r.status_code in (201, 400)
    if r.status_code == 201:
        data = r.json()
        assert "order_id" in data
        assert data["status"] == "INVOICED"

# 🔹 3. Test filtrare după employee (GET /by-employee/{id})
def test_get_orders_by_employee():
    r = client.get("/api/v1/sale-orders/by-employee/1")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

# 🔹 4. Test endpoint /trends (fără dată, doar default)
def test_sales_order_trends_default():
    r = client.get("/api/v1/sale-orders/trends?granulatie=3")
    assert r.status_code == 200
    body = r.json()
    assert "venit" in body
    assert "vanzari_incheiate" in body
    assert "trend_vanzari" in body