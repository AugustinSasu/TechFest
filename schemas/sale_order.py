# schemas/sale_order.py
# SCHEMAS: sale_order.py

# ---------------------------
# Definim DTO-urile (Data Transfer Objects) pentru entitatea `sale_order`.
# Acestea sunt folosite pentru validarea inputului primit de la client și structura de răspuns oferită în API.

# Autor: Alexa Cristian-Valentin
# Data: 09-09-2024

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from decimal import Decimal

# 🔹 Baza comună pentru crearea și răspunsul unui order
class SaleOrderBase(BaseModel):
    dealership_id: int = Field(..., description="ID-ul dealership-ului")
    customer_id: int = Field(..., description="ID-ul clientului")
    salesperson_id: int = Field(..., description="ID-ul agentului de vânzări")
    manager_id: Optional[int] = Field(None, description="ID-ul managerului aprobat")
    order_date: Optional[date] = Field(None, description="Data comenzii")
    status: Optional[str] = Field("OPEN", description="Statusul comenzii")
    total_amount: Optional[Decimal] = Field(None, description="Valoare totală")
    created_by: Optional[str] = Field(None, description="Utilizatorul care a creat comanda")

# 🔹 Pentru creare (POST)
class SaleOrderCreate(SaleOrderBase):
    pass

# 🔹 Pentru update (PUT/PATCH)
class SaleOrderUpdate(BaseModel):
    dealership_id: Optional[int] = None
    customer_id: Optional[int] = None
    salesperson_id: Optional[int] = None
    manager_id: Optional[int] = None
    order_date: Optional[date] = None
    status: Optional[str] = None
    total_amount: Optional[Decimal] = None
    created_by: Optional[str] = None

# 🔹 Pentru răspuns API (GET)
class SaleOrderOut(SaleOrderBase):
    order_id: int

    class Config:
        orm_mode = True  # permite compatibilitate automată SQLAlchemy → Pydantic
