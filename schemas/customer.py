from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class CustomerBase(BaseModel):
    full_name: str = Field(..., max_length=120)
    phone: Optional[str] = Field(None, max_length=40)
    email: Optional[EmailStr] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=120)
    phone: Optional[str] = Field(None, max_length=40)
    email: Optional[EmailStr] = None

class CustomerOut(CustomerBase):
    customer_id: int

    class Config:
        from_attributes = True
