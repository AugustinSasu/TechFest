
# services/sale_order_service.py
# SERVICE: sale_order.py
# -----------------------------
# Conține logica de business pentru comenzi (`sale_order`).
# Interfațează între controller (routes) și repository (SQLAlchemy).

# Autor: Alexa Cristian-Valentin
# Data: 09-09-2024

from typing import List, Optional
from sqlalchemy.orm import Session
from repositories.sale_order_repository import SaleOrderRepository as Repo
from schemas.sale_order import SaleOrderCreate, SaleOrderUpdate
from models.sale_order import SaleOrder

class SaleOrderService:
    @staticmethod
    def create(db: Session, data: SaleOrderCreate) -> SaleOrder:
        return Repo.create(db, data)

    @staticmethod
    def get(db: Session, order_id: int) -> Optional[SaleOrder]:
        return Repo.get(db, order_id)

    @staticmethod
    def list(
        db: Session,
        status: Optional[str],
        customer_id: Optional[int],
        sort: str,
        limit: int,
        offset: int,
    ) -> List[SaleOrder]:
        return Repo.list(db, status=status, customer_id=customer_id, sort=sort, limit=limit, offset=offset)

    @staticmethod
    def update(db: Session, order_id: int, data: SaleOrderUpdate) -> Optional[SaleOrder]:
        return Repo.update(db, order_id, data)

    @staticmethod
    def delete(db: Session, order_id: int) -> bool:
        return Repo.delete(db, order_id)

    @staticmethod
    def list_by_salesperson(db: Session, employee_id: int) -> List[SaleOrder]:
        return Repo.list(db, salesperson_id=employee_id)