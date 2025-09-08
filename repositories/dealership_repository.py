from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, asc, desc
from models.dealership import Dealership
from schemas.dealership import DealershipCreate, DealershipUpdate

class DealershipRepository:
    @staticmethod
    def create(db: Session, data: DealershipCreate) -> Dealership:
        obj = Dealership(**data.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def get(db: Session, dealership_id: int) -> Optional[Dealership]:
        return db.get(Dealership, dealership_id)

    @staticmethod
    def list(
        db: Session,
        q: Optional[str] = None,
        city: Optional[str] = None,
        region: Optional[str] = None,
        sort: str = "asc",       # "asc" | "desc" (după name)
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dealership]:
        stmt = select(Dealership)
        if q:
            stmt = stmt.where(Dealership.name.ilike(f"%{q}%"))
        if city:
            stmt = stmt.where(Dealership.city == city)
        if region:
            stmt = stmt.where(Dealership.region == region)
        order = asc if sort.lower() != "desc" else desc
        stmt = stmt.order_by(order(Dealership.name)).limit(limit).offset(offset)
        return db.execute(stmt).scalars().all()

    @staticmethod
    def update(db: Session, dealership_id: int, data: DealershipUpdate) -> Optional[Dealership]:
        obj = db.get(Dealership, dealership_id)
        if not obj:
            return None
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def delete(db: Session, dealership_id: int) -> bool:
        obj = db.get(Dealership, dealership_id)
        if not obj:
            return False
        db.delete(obj)
        db.commit()
        return True
