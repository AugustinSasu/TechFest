# owner:POP MIRCEA STEFAN
# CRATE_DATE: 2024-06-20 10:40
# LAST MODIFY_DATE: --
# MODIFY BY: --

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, asc, desc, func
from models.vehicle import Vehicle
from schemas.vehicle import VehicleCreate, VehicleUpdate

class VehicleRepository:
    @staticmethod
    def create(db: Session, data: VehicleCreate) -> Vehicle:
        obj = Vehicle(**data.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def get(db: Session, vehicle_id: int) -> Optional[Vehicle]:
        return db.get(Vehicle, vehicle_id)

    @staticmethod
    def list(
        db: Session,
        q: Optional[str] = None,       # caută în model / vin
        model_year: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort: str = "asc",             # după model
        limit: int = 100,
        offset: int = 0,
    ) -> List[Vehicle]:
        stmt = select(Vehicle)
        if q:
            ql = q.lower()
            stmt = stmt.where(
                (func.lower(Vehicle.model).like(f"%{ql}%"))
                | (func.lower(Vehicle.vin).like(f"%{ql}%"))
            )
        if model_year is not None:
            stmt = stmt.where(Vehicle.model_year == model_year)
        if min_price is not None:
            stmt = stmt.where(Vehicle.base_price >= min_price)
        if max_price is not None:
            stmt = stmt.where(Vehicle.base_price <= max_price)

        order = asc if sort.lower() != "desc" else desc
        stmt = stmt.order_by(order(Vehicle.model)).limit(limit).offset(offset)
        return db.execute(stmt).scalars().all()

    @staticmethod
    def update(db: Session, vehicle_id: int, data: VehicleUpdate) -> Optional[Vehicle]:
        obj = db.get(Vehicle, vehicle_id)
        if not obj:
            return None
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def delete(db: Session, vehicle_id: int) -> bool:
        obj = db.get(Vehicle, vehicle_id)
        if not obj:
            return False
        db.delete(obj)
        db.commit()
        return True
