# 📁 api/routes/employee_stats.py
# ✅ ENDPOINT: /employees/stats (GET)
# -------------------------------------
# 📊 Scop: Returnează statistici pe fiecare agent de vânzări
# - nume (din `employee.full_name`)
# - regiune (din `dealership.region`)
# - venit_total: suma vânzărilor auto + servicii
#   - suma din `car_sale_item.unit_price` (vânzări auto)
#   - suma din `service_sale_item.qty * unit_price` (vânzări servicii)
# 🔄 Join-uri multiple și grupare pe `employee`

# -------------------------------------
# autor: Cristian-Valenin Alexa
# data: 2025-09-09

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func, literal_column
from database.session import get_db
from models.employee import Employee
from models.dealership import Dealership
from models.sale_order import SaleOrder
from models.car_sale_item import CarSaleItem
from models.service_sale_item import ServiceSaleItem
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/employees", tags=["employee-stats"])

class EmployeeStatsOut(BaseModel):
    nume: str
    regiune: str
    venit_total: float

    class Config:
        from_attributes = True

@router.get("/stats", response_model=List[EmployeeStatsOut])
def get_employee_stats(db: Session = Depends(get_db)):
    # ⚙️ Build SQL query cu agregări și join-uri
    stmt = (
        select(
            Employee.full_name.label("nume"),
            Dealership.region.label("regiune"),
            func.coalesce(func.sum(CarSaleItem.unit_price), 0) +
            func.coalesce(func.sum(ServiceSaleItem.qty * ServiceSaleItem.unit_price), 0)
        ).label("venit_total")
        .select_from(Employee)
        .join(Dealership, Employee.dealership_id == Dealership.dealership_id)
        .join(SaleOrder, SaleOrder.salesperson_id == Employee.employee_id)
        .outerjoin(CarSaleItem, CarSaleItem.order_id == SaleOrder.order_id)
        .outerjoin(ServiceSaleItem, ServiceSaleItem.order_id == SaleOrder.order_id)
        .group_by(Employee.full_name, Dealership.region)
    )

    result = db.execute(stmt).mappings().all()
    return [EmployeeStatsOut(**row) for row in result]