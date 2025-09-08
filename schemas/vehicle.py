from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class VehicleBase(BaseModel):
    vin: Optional[str] = Field(default=None, max_length=32)
    model: str = Field(..., max_length=60)
    trim_level: Optional[str] = Field(default=None, max_length=60)
    model_year: Optional[int] = None
    base_price: Optional[Decimal] = None

class VehicleCreate(VehicleBase):
    pass

class VehicleUpdate(BaseModel):
    vin: Optional[str] = Field(default=None, max_length=32)
    model: Optional[str] = Field(default=None, max_length=60)
    trim_level: Optional[str] = Field(default=None, max_length=60)
    model_year: Optional[int] = None
    base_price: Optional[Decimal] = None

class VehicleOut(VehicleBase):
    vehicle_id: int
