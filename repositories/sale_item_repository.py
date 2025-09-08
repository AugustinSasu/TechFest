from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, asc, desc
from models.sale_item import SaleItem
from schemas.sale_item import SaleItemCreate, SaleItemUpdate

class SaleItemRepository:
    @staticmethod
    def create(db: Session, data: SaleItemCreate) -> SaleItem:
        obj = SaleItem(**data.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def get(db: Session, item_id: int) -> Optional[SaleItem]:
        return db.get(SaleItem, item_id)

    @staticmethod
    def list(
        db: Session,
        order_id: Optional[int] = None,
        item_type: Optional[str] = None,  # 'CAR' | 'SERVICE'
        sort: str = "asc",                # după item_id
        limit: int = 100,
        offset: int = 0,
    ) -> List[SaleItem]:
        stmt = select(SaleItem)
        if order_id is not None:
            stmt = stmt.where(SaleItem.order_id == order_id)
        if item_type is not None:
            stmt = stmt.where(SaleItem.item_type == item_type)
        order = asc if sort.lower() != "desc" else desc
        stmt = stmt.order_by(order(SaleItem.item_id)).limit(limit).offset(offset)
        return db.execute(stmt).scalars().all()

    @staticmethod
    def update(db: Session, item_id: int, data: SaleItemUpdate) -> Optional[SaleItem]:
        obj = db.get(SaleItem, item_id)
        if not obj:
            return None
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def delete(db: Session, item_id: int) -> bool:
        obj = db.get(SaleItem, item_id)
        if not obj:
            return False
        db.delete(obj)
        db.commit()
        return True
