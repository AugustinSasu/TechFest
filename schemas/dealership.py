# owner:POP MIRCEA STEFAN
# CRATE_DATE: 2024-06-20 10:40
# LAST MODIFY_DATE: --
# MODIFY BY: --


from pydantic import BaseModel, Field
from typing import Optional

class DealershipBase(BaseModel):
    name: str = Field(..., max_length=100)
    city: Optional[str] = Field(None, max_length=80)
    region: Optional[str] = Field(None, max_length=80)

class DealershipCreate(DealershipBase):
    pass

class DealershipUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=80)
    region: Optional[str] = Field(None, max_length=80)

class DealershipOut(DealershipBase):
    dealership_id: int

    class Config:
        from_attributes = True  # permite returnarea directă a ORM objects
