# owner:POP MIRCEA STEFAN
# CRATE_DATE: 2024-06-20 10:40
# LAST MODIFY_DATE: --
# MODIFY BY: --
# services/car_sale_item_service.py
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from schemas.car_sale_item import CarSaleItemCreate, CarSaleItemUpdate
from models.car_sale_item import CarSaleItem
from repositories.car_sale_item_repository import CarSaleItemRepository

class CarSaleItemService:
    def __init__(self, repo: CarSaleItemRepository | None = None):
        self.repo = repo or CarSaleItemRepository()

    def create(self, db: Session, payload: CarSaleItemCreate) -> CarSaleItem:
        try:
            return self.repo.create(db, data=payload.model_dump())
        except IntegrityError:
            # cel mai probabil încalcă UNIQUE(order_id, vehicle_id) sau FK
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate (order_id, vehicle_id) or FK violation")

    def get(self, db: Session, item_id: int) -> Optional[CarSaleItem]:
        return self.repo.get(db, item_id=item_id)

    def update(self, db: Session, item_id: int, payload: CarSaleItemUpdate) -> Optional[CarSaleItem]:
        data = {k: v for k, v in payload.model_dump().items() if v is not None}
        try:
            return self.repo.update(db, item_id=item_id, data=data)
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate (order_id, vehicle_id) or FK violation")

    def delete(self, db: Session, item_id: int) -> bool:
        return self.repo.delete(db, item_id=item_id)

    def list(
        self,
        db: Session,
        *,
        order_id: Optional[int],
        min_price: Optional[float],
        max_price: Optional[float],
        sort_by: str,
        sort: str,
        skip: int,
        limit: int,
    ) -> List[CarSaleItem]:
        # normalizează parametrii
        sort_by = (sort_by or "item_id").lower()
        if sort_by not in {"item_id", "order_id"}:
            sort_by = "item_id"
        sort = (sort or "asc").lower()
        if sort not in {"asc", "desc"}:
            sort = "asc"
        return self.repo.list(
            db,
            order_id=order_id,
            min_price=min_price,
            max_price=max_price,
            sort_by=sort_by,
            sort=sort,
            skip=skip,
            limit=limit,
        )
