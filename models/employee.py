# models/employee.py
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey
from database.engine import Base  # folosește Base-ul tău existent

class Employee(Base):
    __tablename__ = "employee"

    employee_id:   Mapped[int]  = mapped_column(Integer, primary_key=True)
    db_username:   Mapped[str]  = mapped_column(String(30), unique=True, nullable=False)
    full_name:     Mapped[str]  = mapped_column(String(120), nullable=False)
    role_code:     Mapped[str]  = mapped_column(String(10), nullable=False)  # 'SALES' | 'MANAGER' (validat în DB)
    dealership_id: Mapped[int]  = mapped_column(ForeignKey("dealership.dealership_id"), nullable=False)

    # adăugată în DB prin ALTER TABLE employee ADD (password VARCHAR2(255))
    password:      Mapped[str | None] = mapped_column(String(255))
