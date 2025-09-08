from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse, PlainTextResponse
from typing import List, Optional
from sqlalchemy.orm import Session

from database.session import get_db
from services.dealership_service import DealershipService as Svc
from schemas.dealership import DealershipCreate, DealershipUpdate, DealershipOut

router = APIRouter(prefix="/dealerships", tags=["dealerships"])

@router.post("", response_model=DealershipOut, status_code=201)
def create_dealership(payload: DealershipCreate, db: Session = Depends(get_db)):
    return Svc.create(db, payload)

@router.get("/{dealership_id}", response_model=DealershipOut)
def get_dealership(dealership_id: int, db: Session = Depends(get_db)):
    obj = Svc.get(db, dealership_id)
    if not obj:
        raise HTTPException(404, "Dealership not found")
    return obj

@router.get("", response_model=List[DealershipOut])
def list_dealerships(
    q: Optional[str] = None,
    city: Optional[str] = None,
    region: Optional[str] = None,
    sort: str = "asc",          # "asc" / "desc" după name
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    return Svc.list(db, q=q, city=city, region=region, sort=sort, limit=limit, offset=offset)

@router.put("/{dealership_id}", response_model=DealershipOut)
def update_dealership(dealership_id: int, payload: DealershipUpdate, db: Session = Depends(get_db)):
    obj = Svc.update(db, dealership_id, payload)
    if not obj:
        raise HTTPException(404, "Dealership not found")
    return obj

@router.delete("/{dealership_id}", status_code=204)
def delete_dealership(dealership_id: int, db: Session = Depends(get_db)):
    ok = Svc.delete(db, dealership_id)
    if not ok:
        raise HTTPException(404, "Dealership not found")
    return Response(status_code=204)

# ---- Exports ----
@router.get("/_export/json")
def export_json(db: Session = Depends(get_db)):
    return JSONResponse(content=Svc.export_json(db))

@router.get("/_export/txt")
def export_txt(db: Session = Depends(get_db)):
    return PlainTextResponse(content=Svc.export_txt(db), media_type="text/plain")
