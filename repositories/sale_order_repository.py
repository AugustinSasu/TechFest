# repositories/sale_order_repository.py
# REPOSITORY: sale_order.py
# -----------------------------
# Conține toate metodele de acces la baza de date pentru entitatea `sale_order`.
# Se ocupă cu operațiuni CRUD și listare cu filtre opționale (ex: status, client etc.)

# Autor: Alexa Cristian-Valentin
# Data: 09-09-2024
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, asc, desc
from models.sale_order import SaleOrder
from schemas.sale_order import SaleOrderCreate, SaleOrderUpdate

class SaleOrderRepository:
    @staticmethod
    def create(db: Session, data: SaleOrderCreate) -> SaleOrder:
        obj = SaleOrder(**data.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def get(db: Session, order_id: int) -> Optional[SaleOrder]:
        return db.get(SaleOrder, order_id)

    @staticmethod
    def list(
        db: Session,
        status: Optional[str] = None,
        customer_id: Optional[int] = None,
        sort: str = "asc",
        limit: int = 100,
        offset: int = 0,
    ) -> List[SaleOrder]:
        stmt = select(SaleOrder)
        if status:
            stmt = stmt.where(SaleOrder.status == status)
        if customer_id:
            stmt = stmt.where(SaleOrder.customer_id == customer_id)

        order = asc if sort.lower() != "desc" else desc
        stmt = stmt.order_by(order(SaleOrder.order_id)).limit(limit).offset(offset)
        return db.execute(stmt).scalars().all()

    @staticmethod
    def update(db: Session, order_id: int, data: SaleOrderUpdate) -> Optional[SaleOrder]:
        obj = db.get(SaleOrder, order_id)
        if not obj:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def delete(db: Session, order_id: int) -> bool:
        obj = db.get(SaleOrder, order_id)
        if not obj:
            return False
        db.delete(obj)
        db.commit()
        return True
