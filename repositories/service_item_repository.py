
# owner:VALENTIN-ALEXA
# CRATE_DATE: 2024-06-20 10:40
# LAST MODIFY_DATE: --
# MODIFY BY: --

# repositories/service_item_repository.py
# REPOSITORY: service_item.py


from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, asc, desc, func
from models.service_item import ServiceItem
from schemas.service_item import ServiceItemCreate, ServiceItemUpdate

class ServiceItemRepository:
    @staticmethod
    def create(db: Session, data: ServiceItemCreate) -> ServiceItem:
        obj = ServiceItem(**data.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def get(db: Session, service_id: int) -> Optional[ServiceItem]:
        return db.get(ServiceItem, service_id)

    @staticmethod
    def list(
        db: Session,
        q: Optional[str] = None,              # căutare text
        service_type: Optional[str] = None,   # filtrare tip
        sort: str = "asc",
        limit: int = 100,
        offset: int = 0,
    ) -> List[ServiceItem]:
        stmt = select(ServiceItem)
        if q:
            stmt = stmt.where(func.lower(ServiceItem.name).like(f"%{q.lower()}%"))
        if service_type:
            stmt = stmt.where(ServiceItem.service_type == service_type)

        order = asc if sort.lower() != "desc" else desc
        stmt = stmt.order_by(order(ServiceItem.name)).limit(limit).offset(offset)
        return db.execute(stmt).scalars().all()

    @staticmethod
    def update(db: Session, service_id: int, data: ServiceItemUpdate) -> Optional[ServiceItem]:
        obj = db.get(ServiceItem, service_id)
        if not obj:
            return None
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def delete(db: Session, service_id: int) -> bool:
        obj = db.get(ServiceItem, service_id)
        if not obj:
            return False
        db.delete(obj)
        db.commit()
        return True
