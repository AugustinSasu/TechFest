# schemas/car_sale_item.py
from typing import Optional
from pydantic import BaseModel, Field

class CarSaleItemBase(BaseModel):
    order_id: int
    vehicle_id: int
    unit_price: float = Field(..., ge=0)

class CarSaleItemCreate(CarSaleItemBase):
    pass

class CarSaleItemUpdate(BaseModel):
    order_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    unit_price: Optional[float] = Field(None, ge=0)

class CarSaleItemOut(BaseModel):
    item_id: int
    order_id: int
    vehicle_id: int
    unit_price: float

    class Config:
        from_attributes = True
