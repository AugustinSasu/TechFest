# -----------------------------------------------------------------
# Acest fișier definește logica de business pentru entitatea "sale_item" (produse vândute).
# Fiecare sale_item reprezintă o linie dintr-o comandă de vânzare: fie o mașină (CAR), fie un serviciu (SERVICE).
# Layer-ul service gestionează validarea și coordonează accesul la `SaleItemRepository`.
#
# Autor: Cristian-Valentin Alexa
# Data: 14 Aprilie 2024 
# Ora: 15:01
# -----------------------------------------------------------------

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from repositories.sale_item_repository import SaleItemRepository as Repo
from schemas.sale_item import SaleItemCreate, SaleItemUpdate
from models.sale_item import SaleItem
from decimal import Decimal

class SaleItemService:
    @staticmethod
    def create(db: Session, data: SaleItemCreate) -> SaleItem:
        """
        Creează un obiect SaleItem, cu validări în funcție de tip (CAR/SERVICE).
        CAR -> trebuie completat vehicle_id
        SERVICE -> trebuie completat service_id
        """
        if data.item_type == "CAR" and not data.vehicle_id:
            raise ValueError("CAR items require vehicle_id")
        if data.item_type == "SERVICE" and not data.service_id:
            raise ValueError("SERVICE items require service_id")
        return Repo.create(db, data)

    @staticmethod
    def get(db: Session, item_id: int) -> Optional[SaleItem]:
        """
        Returnează item-ul de vânzare după ID.
        """
        return Repo.get(db, item_id)

    @staticmethod
    def list(
        db: Session,
        order_id: Optional[int],
        item_type: Optional[str],  # CAR / SERVICE
        sort: str,
        limit: int,
        offset: int,
    ) -> List[SaleItem]:
        """
        Returnează o listă de sale_items filtrată și ordonată.
        """
        return Repo.list(db, order_id=order_id, item_type=item_type, sort=sort, limit=limit, offset=offset)

    @staticmethod
    def update(db: Session, item_id: int, data: SaleItemUpdate) -> Optional[SaleItem]:
        """
        Actualizează un sale_item existent, dacă este găsit.
        """
        return Repo.update(db, item_id, data)

    @staticmethod
    def delete(db: Session, item_id: int) -> bool:
        """
        Șterge linia de vânzare din DB.
        """
        return Repo.delete(db, item_id)

    @staticmethod
    def export_json(db: Session) -> List[Dict[str, Any]]:
        """
        Exportă toate sale_items ca JSON serializabil.
        """
        rows = Repo.list(db, limit=10_000, offset=0, sort="asc")
        return [
            {
                "item_id": r.item_id,
                "order_id": r.order_id,
                "item_type": r.item_type,
                "vehicle_id": r.vehicle_id,
                "service_id": r.service_id,
                "qty": float(r.qty),
                "unit_price": float(r.unit_price),
                "line_total": float(SaleItemService.compute_line_total(r.qty, r.unit_price))
            }
            for r in rows
        ]

    @staticmethod
    def export_txt(db: Session) -> str:
        """
        Exportă toate sale_items sub formă de text tabelar (.txt).
        """
        rows = Repo.list(db, limit=10_000, offset=0, sort="asc")
        lines = ["item_id | order_id | item_type | vehicle_id | service_id | qty | unit_price | line_total"]
        for r in rows:
            total = SaleItemService.compute_line_total(r.qty, r.unit_price)
            lines.append(
                f"{r.item_id} | {r.order_id} | {r.item_type} | {r.vehicle_id or ''} | {r.service_id or ''} | "
                f"{r.qty} | {r.unit_price} | {total}"
            )
        return "\n".join(lines)

    @staticmethod
    def compute_line_total(qty: Decimal, unit_price: Decimal) -> Decimal:
        """
        Calculează totalul pentru o linie: qty * unit_price
        """
        return (qty or Decimal("0")) * (unit_price or Decimal("0"))