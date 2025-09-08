# schemas/service_sale_item.py
#  service_sale_item.py
# --------------------------------- -------------------------------

# Fișierul definește toate DTO-urile (Data Transfer Objects) pentru entitatea `service_sale_item`.
# Aceste clase Pydantic sunt folosite pentru validare input și structurare output în API.

# Autor: Cristian-Valentin Alexa
# Data: 14 Aprilie 2024

#------------------------------------------------- ------------  

from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

# 🔹 Schema de bază comună
class ServiceSaleItemBase(BaseModel):
    order_id: int = Field(..., description="ID-ul comenzii în care se vinde serviciul")
    service_id: int = Field(..., description="ID-ul serviciului vândut")
    qty: Decimal = Field(default=1, gt=0, description="Cantitatea de servicii achiziționate")
    unit_price: Decimal = Field(..., ge=0, description="Preț unitar per serviciu")

# 🔹 DTO pentru creare (POST)
class ServiceSaleItemCreate(ServiceSaleItemBase):
    pass

# 🔹 DTO pentru update (PUT/PATCH)
class ServiceSaleItemUpdate(BaseModel):
    qty: Optional[Decimal] = Field(None, gt=0)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    service_id: Optional[int] = None

# 🔹 DTO pentru răspuns (GET / list)
class ServiceSaleItemOut(ServiceSaleItemBase):
    item_id: int = Field(..., description="ID-ul liniei de vânzare")
    line_total: Decimal = Field(..., description="Total = qty * unit_price")

    class Config:
        orm_mode = True  # permite conversia automată din SQLAlchemy -> Pydantic
