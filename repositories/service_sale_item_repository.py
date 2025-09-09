# 📁 repositories/service_sale_item_repository.py
# ✅ REPOSITORY: service_sale_item.py
# ------------------------------------
# Acest fișier definește accesul la date pentru entitatea `service_sale_item`.
# Reprezintă stratul care interacționează direct cu baza de date prin SQLAlchemy.
# Include metode CRUD și listare cu filtre opționale.
# Suportă și filtrare după salesperson_id (JOIN cu sale_order).

# Autor: Cristian-Valentin Alexa
# Data: 14 Aprilie 2024

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, asc, desc
from models.service_sale_item import ServiceSaleItem
from schemas.service_sale_item import ServiceSaleItemCreate, ServiceSaleItemUpdate
from models.sale_order import SaleOrder

class ServiceSaleItemRepository:
    @staticmethod
    def create(db: Session, data: ServiceSaleItemCreate) -> ServiceSaleItem:
        """
        Creează o linie de vânzare pentru un serviciu.
        """
        obj = ServiceSaleItem(**data.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def get(db: Session, item_id: int) -> Optional[ServiceSaleItem]:
        """
        Returnează un `ServiceSaleItem` după ID.
        """
        return db.get(ServiceSaleItem, item_id)

    @staticmethod
    def list(
        db: Session,
        order_id: Optional[int] = None,
        service_id: Optional[int] = None,
        salesperson_id: Optional[int] = None,
        sort: str = "asc",
        limit: int = 100,
        offset: int = 0,
    ) -> List[ServiceSaleItem]:
        """
        Returnează o listă de servicii vândute, filtrate după order_id, service_id sau salesperson_id.
        Dacă este specificat `salesperson_id`, se face JOIN cu `sale_order`.
        """
        stmt = select(ServiceSaleItem)

        if salesperson_id is not None:
            stmt = stmt.join(SaleOrder, ServiceSaleItem.order_id == SaleOrder.order_id)
            stmt = stmt.where(SaleOrder.salesperson_id == salesperson_id)

        if order_id is not None:
            stmt = stmt.where(ServiceSaleItem.order_id == order_id)
        if service_id is not None:
            stmt = stmt.where(ServiceSaleItem.service_id == service_id)

        order = asc if sort.lower() != "desc" else desc
        stmt = stmt.order_by(order(ServiceSaleItem.item_id)).limit(limit).offset(offset)
        return db.execute(stmt).scalars().all()

    @staticmethod
    def update(db: Session, item_id: int, data: ServiceSaleItemUpdate) -> Optional[ServiceSaleItem]:
        """
        Actualizează un `ServiceSaleItem` existent. Doar câmpurile setate în update vor fi modificate.
        """
        obj = db.get(ServiceSaleItem, item_id)
        if not obj:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def delete(db: Session, item_id: int) -> bool:
        """
        Șterge o linie de vânzare din baza de date. Returnează True dacă a existat.
        """
        obj = db.get(ServiceSaleItem, item_id)
        if not obj:
            return False
        db.delete(obj)
        db.commit()
        return True
