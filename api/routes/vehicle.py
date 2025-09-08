from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from database.session import get_db
from services.vehicle_service import VehicleService
from schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleOut

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

@router.get("/", response_model=List[VehicleOut])
def list_vehicles(
    q: Optional[str] = Query(None),
    model_year: Optional[int] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    sort: str = Query("asc", pattern="^(asc|desc)$"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    rows = VehicleService.list(db, q, model_year, min_price, max_price, sort, limit, offset)
    return [VehicleOut(vehicle_id=r.vehicle_id, vin=r.vin, model=r.model,
                       trim_level=r.trim_level, model_year=r.model_year, base_price=r.base_price) for r in rows]

@router.get("/{vehicle_id}", response_model=VehicleOut)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    obj = VehicleService.get(db, vehicle_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return VehicleOut(vehicle_id=obj.vehicle_id, vin=obj.vin, model=obj.model,
                      trim_level=obj.trim_level, model_year=obj.model_year, base_price=obj.base_price)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=VehicleOut)
def create_vehicle(payload: VehicleCreate, db: Session = Depends(get_db)):
    obj = VehicleService.create(db, payload)
    return VehicleOut(vehicle_id=obj.vehicle_id, vin=obj.vin, model=obj.model,
                      trim_level=obj.trim_level, model_year=obj.model_year, base_price=obj.base_price)

@router.put("/{vehicle_id}", response_model=VehicleOut)
def update_vehicle(vehicle_id: int, payload: VehicleUpdate, db: Session = Depends(get_db)):
    obj = VehicleService.update(db, vehicle_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return VehicleOut(vehicle_id=obj.vehicle_id, vin=obj.vin, model=obj.model,
                      trim_level=obj.trim_level, model_year=obj.model_year, base_price=obj.base_price)

@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    ok = VehicleService.delete(db, vehicle_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return
