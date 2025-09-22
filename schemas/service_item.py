# owner:POP MIRCEA STEFAN
# CRATE_DATE: 2024-06-20 10:40
# LAST MODIFY_DATE: --
# MODIFY BY: --
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class ServiceItemBase(BaseModel):
    service_type: str = Field(..., max_length=24)  # validate în service
    name: str = Field(..., max_length=120)
    description: Optional[str] = Field(default=None, max_length=4000)
    list_price: Optional[Decimal] = None

class ServiceItemCreate(ServiceItemBase):
    pass

class ServiceItemUpdate(BaseModel):
    service_type: Optional[str] = Field(default=None, max_length=24)
    name: Optional[str] = Field(default=None, max_length=120)
    description: Optional[str] = Field(default=None, max_length=4000)
    list_price: Optional[Decimal] = None

class ServiceItemOut(ServiceItemBase):
    service_id: int
