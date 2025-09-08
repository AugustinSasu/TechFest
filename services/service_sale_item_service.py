# services/service_sale_item_service.py
# service_sale_item.py
# --------------------------------------

# Acest fișier implementează logica de business pentru `service_sale_item`,
# apelând repository-ul și oferind metode utile pentru API.
# Include calculul `line_total` și exporturi JSON / TXT pentru rapoarte.

# Autor: Cristian-Valentin Alexa
# Data: 14 Aprilie 2024

# --------------------------------------

from typing import List, Optional, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from repositories.service_sale_item_repository import ServiceSaleItemRepository as Repo
from schemas.service_sale_item import ServiceSaleItemCreate, ServiceSaleItemUpdate
from models.service_sale_item import ServiceSaleItem

class ServiceSaleItemService:
    @staticmethod
    def create(db: Session, data: ServiceSaleItemCreate) -> ServiceSaleItem:
        return Repo.create(db, data)

    @staticmethod
    def get(db: Session, item_id: int) -> Optional[ServiceSaleItem]:
        return Repo.get(db, item_id)

    @staticmethod
    def list(
        db: Session,
        order_id: Optional[int],
        service_id: Optional[int],
        sort: str,
        limit: int,
        offset: int,
    ) -> List[ServiceSaleItem]:
        return Repo.list(
            db,
            order_id=order_id,
            service_id=service_id,
            sort=sort,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def update(db: Session, item_id: int, data: ServiceSaleItemUpdate) -> Optional[ServiceSaleItem]:
        return Repo.update(db, item_id, data)

    @staticmethod
    def delete(db: Session, item_id: int) -> bool:
        return Repo.delete(db, item_id)

    @staticmethod
    def compute_line_total(qty: Decimal, unit_price: Decimal) -> Decimal:
        """
        Calculează totalul pentru un serviciu: qty * unit_price
        Este folosit pentru a include `line_total` în răspunsul API.
        """
        return (qty or Decimal("0")) * (unit_price or Decimal("0"))

    @staticmethod
    def export_json(db: Session) -> List[Dict[str, Any]]:
        rows = Repo.list(db, limit=10_000, offset=0, sort="asc")
        return [
            {
                "item_id": r.item_id,
                "order_id": r.order_id,
                "service_id": r.service_id,
                "qty": float(r.qty),
                "unit_price": float(r.unit_price),
                "line_total": float(ServiceSaleItemService.compute_line_total(r.qty, r.unit_price))
            }
            for r in rows
        ]

    @staticmethod
    def export_txt(db: Session) -> str:
        rows = Repo.list(db, limit=10_000, offset=0, sort="asc")
        lines = ["item_id | order_id | service_id | qty | unit_price | line_total"]
        for r in rows:
            total = ServiceSaleItemService.compute_line_total(r.qty, r.unit_price)
            lines.append(
                f"{r.item_id} | {r.order_id} | {r.service_id} | {r.qty} | {r.unit_price} | {total}"
            )
        return "\n".join(lines)
