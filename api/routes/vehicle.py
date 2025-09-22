# --------------------------------------------------------------
# Acest fișier definește toate endpointurile HTTP pentru entitatea "vehicle".
# Este conectat la `VehicleService` și mapat sub prefixul /vehicles prin FastAPI Router.
# Fiecare endpoint este documentat cu tipuri de date, scop și validări de parametri.
# Autor: Cristian-Valentin Alexa
# Data: 14 Aprilie 2024
#-------------------------------------------------------------

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database.session import get_db
from services.vehicle_service import VehicleService
from schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleOut
#the full route to the endpoint will be api/vehicles
router = APIRouter(prefix="/vehicles", tags=["vehicles"])

@router.get("/", response_model=List[VehicleOut])
def list_vehicles(
    q: Optional[str] = Query(None, description="Caută în VIN sau model"),
    model_year: Optional[int] = Query(None, ge=1900, le=2100),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    sort: str = Query("asc", pattern="^(asc|desc)$"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Returnează o listă de vehicule filtrate și ordonate.
    Suportă parametri opționali: q, an model, preț minim/maxim, sortare, paginare.
    """
    return VehicleService.list(db, q, model_year, min_price, max_price, sort, limit, offset)

@router.get("/{vehicle_id}", response_model=VehicleOut)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    """
    Returnează un vehicul specific după ID. 404 dacă nu există.
    """
    obj = VehicleService.get(db, vehicle_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return obj

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=VehicleOut)
def create_vehicle(payload: VehicleCreate, db: Session = Depends(get_db)):
    """
    Creează un nou vehicul în sistem.
    """
    return VehicleService.create(db, payload)

@router.put("/{vehicle_id}", response_model=VehicleOut)
def update_vehicle(vehicle_id: int, payload: VehicleUpdate, db: Session = Depends(get_db)):
    """
    Actualizează vehiculul existent.
    """
    obj = VehicleService.update(db, vehicle_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return obj

@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    """
    Șterge vehiculul din baza de date.
    """
    ok = VehicleService.delete(db, vehicle_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return

@router.get("/export/json", response_model=List[dict])
def export_vehicles_json(db: Session = Depends(get_db)):
    """
    Exportă toate vehiculele ca listă JSON.
    """
    return VehicleService.export_json(db)

@router.get("/export/txt", response_model=str)
def export_vehicles_txt(db: Session = Depends(get_db)):
    """
    Exportă toate vehiculele ca text tabelar (.txt).
    """
    return VehicleService.export_txt(db)