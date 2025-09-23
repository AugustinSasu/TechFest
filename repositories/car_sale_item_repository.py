# repositories/car_sale_item_repository.py
# owner:POP MIRCEA STEFAN
# CRATE_DATE: 2024-06-20 10:40
# LAST MODIFY_DATE: --
# MODIFY BY: --
#descriere: repository pentru entitatea CarSaleItem
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, asc, desc, and_
from sqlalchemy.exc import IntegrityError
from models.car_sale_item import CarSaleItem

class CarSaleItemRepository:
    def create(self, db: Session, *, data: dict) -> CarSaleItem:
        obj = CarSaleItem(**data)
        db.add(obj)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise
        db.refresh(obj)
        return obj

    def get(self, db: Session, *, item_id: int) -> Optional[CarSaleItem]:
        return db.get(CarSaleItem, item_id)

    def update(self, db: Session, *, item_id: int, data: dict) -> Optional[CarSaleItem]:
        obj = self.get(db, item_id=item_id)
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise
        db.refresh(obj)
        return obj

    def delete(self, db: Session, *, item_id: int) -> bool:
        obj = self.get(db, item_id=item_id)
        if not obj:
            return False
        db.delete(obj)
        db.commit()
        return True

    def list(
        self,
        db: Session,
        *,
        order_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: str = "item_id",      # 'item_id' | 'order_id'
        sort: str = "asc",             # 'asc' | 'desc'
        skip: int = 0,
        limit: int = 100,
    ) -> List[CarSaleItem]:
        stmt = select(CarSaleItem)
        conds = []
        if order_id is not None:
            conds.append(CarSaleItem.order_id == order_id)
        if min_price is not None:
            conds.append(CarSaleItem.unit_price >= min_price)
        if max_price is not None:
            conds.append(CarSaleItem.unit_price <= max_price)
        if conds:
            stmt = stmt.where(and_(*conds))

        sort_by = (sort_by or "item_id").lower()
        col = CarSaleItem.item_id if sort_by != "order_id" else CarSaleItem.order_id
        order = asc(col) if (sort or "asc").lower() != "desc" else desc(col)

        stmt = stmt.order_by(order).offset(skip).limit(limit)
        return list(db.scalars(stmt))
