# owner:POP MIRCEA STEFAN
# CRATE_DATE: 2024-06-20 10:40
# LAST MODIFY_DATE: --
# MODIFY BY: --
# schemas/employee.py
from typing import Optional, Literal
from pydantic import BaseModel, Field

RoleLiteral = Literal["SALES", "MANAGER"]

class EmployeeBase(BaseModel):
    db_username: str = Field(..., min_length=1, max_length=30)
    full_name: str = Field(..., max_length=120)
    role_code: RoleLiteral
    dealership_id: int

class EmployeeCreate(EmployeeBase):
    password: Optional[str] = Field(None, max_length=255)

class EmployeeRegister(BaseModel):
    db_username: str = Field(..., min_length=1, max_length=30)
    full_name: str = Field(..., max_length=120)
    role_code: RoleLiteral
    dealership_id: int
    password: str = Field(..., min_length=1, max_length=255)

class EmployeeUpdate(BaseModel):
    db_username: Optional[str] = Field(None, min_length=1, max_length=30)
    full_name: Optional[str] = Field(None, max_length=120)
    role_code: Optional[RoleLiteral] = None
    dealership_id: Optional[int] = None
    password: Optional[str] = Field(None, max_length=255)

class EmployeeOut(BaseModel):
    employee_id: int
    db_username: str
    full_name: str
    role_code: RoleLiteral
    dealership_id: int
    class Config:
        from_attributes = True

# ---- Sign-in (simplu, fără token) ----
class SignInRequest(BaseModel):
    db_username: str
    password: str

class SignInResponse(BaseModel):
    authenticated: bool
    employee: Optional[EmployeeOut] = None
