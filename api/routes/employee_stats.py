# owner:valentin-alexa
# CRATE_DATE: 2024-06-20 10:40
# LAST MODIFY_DATE: --
# MODIFY BY: --

# ✅ Endpoint:
#     GET /employees/stats
#
# 🎯 Purpose:
#     - Aggregate revenue per sales agent (employee).
#     - Return results grouped by employee name and dealership region.
#
# 📊 Data sources:
#     - Employee.full_name → sales agent's full name.
#     - Dealership.region → geographic region of the employee's dealership.
#     - Revenue calculation:
#         * Car sales revenue: SUM(car_sale_item.unit_price)
#         * Service sales revenue: SUM(service_sale_item.qty * unit_price)
#         * Total revenue = car sales + service sales
#
# 🔄 Query design:
#     - Joins multiple tables: Employee, Dealership, SaleOrder, CarSaleItem, ServiceSaleItem.
#     - Uses SQLAlchemy `select()` with aggregate functions (`sum`, `coalesce`).
#     - Groups results by employee and region.
#     - Outer joins for items ensure employees without certain sales types are still included.
#
# 📦 Output model (EmployeeStatsOut):
#     - nume (string)    → employee’s full name
#     - regiune (string) → dealership region
#     - venit_total (float) → total revenue (cars + services)
#
# ⚙️ Implementation notes:
#     - Service layer is not used here; the query is built directly in the router for performance and readability.
#     - For larger datasets, consider pagination or async queries.
#     - Security: endpoint is read-only, no sensitive fields exposed.
#     - Extendable: can add filters (date range, dealership, etc.) or more KPIs later.
# """

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

#the full route to the endpoint will be api/employees
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