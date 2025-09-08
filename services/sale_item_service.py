from typing import List, Optional
from sqlalchemy.orm import Session
from repositories.sale_item_repository import SaleItemRepository as Repo
from schemas.sale_item import SaleItemCreate, SaleItemUpdate
from models.sale_item import SaleItem
from decimal import Decimal

class SaleItemService:
    @staticmethod
    def create(db: Session, data: SaleItemCreate) -> SaleItem:
        # Validare business simplă: exact un FK în funcție de item_type
        if data.item_type == "CAR" and not data.vehicle_id:
            raise ValueError("CAR items require vehicle_id")
        if data.item_type == "SERVICE" and not data.service_id:
            raise ValueError("SERVICE items require service_id")
        return Repo.create(db, data)

    @staticmethod
    def get(db: Session, item_id: int) -> Optional[SaleItem]:
        return Repo.get(db, item_id)

    @staticmethod
    def list(
        db: Session,
        order_id: Optional[int],
        item_type: Optional[str],
        sort: str,
        limit: int,
        offset: int,
    ) -> List[SaleItem]:
        return Repo.list(db, order_id=order_id, item_type=item_type, sort=sort, limit=limit, offset=offset)

    @staticmethod
    def update(db: Session, item_id: int, data: SaleItemUpdate) -> Optional[SaleItem]:
        return Repo.update(db, item_id, data)

    @staticmethod
    def delete(db: Session, item_id: int) -> bool:
        return Repo.delete(db, item_id)

    @staticmethod
    def compute_line_total(qty: Decimal, unit_price: Decimal) -> Decimal:
        return (qty or Decimal("0")) * (unit_price or Decimal("0"))
