# owner:POP MIRCEA STEFAN
# CRATE_DATE: 2024-06-20 10:40
# LAST MODIFY_DATE: --
# MODIFY BY: --


from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from repositories.dealership_repository import DealershipRepository as Repo
from schemas.dealership import DealershipCreate, DealershipUpdate
from models.dealership import Dealership

class DealershipService:
    @staticmethod
    def create(db: Session, data: DealershipCreate) -> Dealership:
        return Repo.create(db, data)

    @staticmethod
    def get(db: Session, dealership_id: int) -> Optional[Dealership]:
        return Repo.get(db, dealership_id)

    @staticmethod
    def list(  # păstrăm numele, dar grijă la adnotări mai jos
        db: Session,
        q: Optional[str],
        city: Optional[str],
        region: Optional[str],
        sort: str,
        limit: int,
        offset: int,
    ) -> List[Dealership]:
        return Repo.list(db, q=q, city=city, region=region, sort=sort, limit=limit, offset=offset)

    @staticmethod
    def update(db: Session, dealership_id: int, data: DealershipUpdate) -> Optional[Dealership]:
        return Repo.update(db, dealership_id, data)

    @staticmethod
    def delete(db: Session, dealership_id: int) -> bool:
        return Repo.delete(db, dealership_id)

    @staticmethod
    def export_txt(db: Session) -> str:
        rows = Repo.list(db, limit=10_000, offset=0, sort="asc")
        lines = ["dealership_id | name | city | region"]
        for r in rows:
            lines.append(f"{r.dealership_id} | {r.name} | {r.city or ''} | {r.region or ''}")
        return "\n".join(lines)

    @staticmethod
    def export_json(db: Session) -> List[Dict[str, Any]]:
        rows = Repo.list(db, limit=10_000, offset=0, sort="asc")
        return [
            {"dealership_id": r.dealership_id, "name": r.name, "city": r.city, "region": r.region}
            for r in rows
        ]
