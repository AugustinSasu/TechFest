from pydantic import BaseModel, Field
from typing import Optional, Literal
from decimal import Decimal

ItemType = Literal["CAR", "SERVICE"]

class SaleItemBase(BaseModel):
    order_id: int
    item_type: ItemType
    vehicle_id: Optional[int] = None
    service_id: Optional[int] = None
    qty: Decimal = Field(default=1)
    unit_price: Decimal

class SaleItemCreate(SaleItemBase):
    pass

class SaleItemUpdate(BaseModel):
    vehicle_id: Optional[int] = None
    service_id: Optional[int] = None
    qty: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None

class SaleItemOut(BaseModel):
    item_id: int
    order_id: int
    item_type: ItemType
    vehicle_id: Optional[int]
    service_id: Optional[int]
    qty: Decimal
    unit_price: Decimal
    line_total: Decimal  # calculăm la read (qty * unit_price)
