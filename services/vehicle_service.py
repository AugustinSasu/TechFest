from typing import List, Optional
from sqlalchemy.orm import Session
from repositories.vehicle_repository import VehicleRepository as Repo
from schemas.vehicle import VehicleCreate, VehicleUpdate
from models.vehicle import Vehicle

class VehicleService:
    @staticmethod
    def create(db: Session, data: VehicleCreate) -> Vehicle:
        return Repo.create(db, data)

    @staticmethod
    def get(db: Session, vehicle_id: int) -> Optional[Vehicle]:
        return Repo.get(db, vehicle_id)

    @staticmethod
    def list(
        db: Session,
        q: Optional[str],
        model_year: Optional[int],
        min_price: Optional[float],
        max_price: Optional[float],
        sort: str,
        limit: int,
        offset: int,
    ) -> List[Vehicle]:
        return Repo.list(db, q=q, model_year=model_year, min_price=min_price, max_price=max_price,
                         sort=sort, limit=limit, offset=offset)

    @staticmethod
    def update(db: Session, vehicle_id: int, data: VehicleUpdate) -> Optional[Vehicle]:
        return Repo.update(db, vehicle_id, data)

    @staticmethod
    def delete(db: Session, vehicle_id: int) -> bool:
        return Repo.delete(db, vehicle_id)
