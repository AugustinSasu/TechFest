# owner:POP MIRCEA STEFAN
# CRATE_DATE: 2024-06-20 10:40
# LAST MODIFY_DATE: --
# MODIFY BY: --

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse, PlainTextResponse
from typing import List, Optional
from sqlalchemy.orm import Session

from database.session import get_db
from services.dealership_service import DealershipService as Svc
from schemas.dealership import DealershipCreate, DealershipUpdate, DealershipOut

# Create a router for dealership endpoints, with a prefix and tag for grouping in docs
router = APIRouter(prefix="/dealerships", tags=["dealerships"])

# Create a new dealership
@router.post("", response_model=DealershipOut, status_code=201)
def create_dealership(payload: DealershipCreate, db: Session = Depends(get_db)):
    # Calls the service to create a dealership and returns the created object
    return Svc.create(db, payload)

# Retrieve a dealership by its ID
@router.get("/{dealership_id}", response_model=DealershipOut)
def get_dealership(dealership_id: int, db: Session = Depends(get_db)):
    # Fetches the dealership; raises 404 if not found
    obj = Svc.get(db, dealership_id)
    if not obj:
        raise HTTPException(404, "Dealership not found")
    return obj

# List dealerships with optional filters and pagination
@router.get("", response_model=List[DealershipOut])
def list_dealerships(
    q: Optional[str] = None,      # Search query
    city: Optional[str] = None,   # Filter by city
    region: Optional[str] = None, # Filter by region
    sort: str = "asc",            # Sort order
    limit: int = 100,             # Max results
    offset: int = 0,              # Pagination offset
    db: Session = Depends(get_db),
):
    # Returns a list of dealerships based on filters
    return Svc.list(db, q=q, city=city, region=region, sort=sort, limit=limit, offset=offset)

# Update an existing dealership
@router.put("/{dealership_id}", response_model=DealershipOut)
def update_dealership(dealership_id: int, payload: DealershipUpdate, db: Session = Depends(get_db)):
    # Updates the dealership; raises 404 if not found
    obj = Svc.update(db, dealership_id, payload)
    if not obj:
        raise HTTPException(404, "Dealership not found")
    return obj

# Delete a dealership by ID
@router.delete("/{dealership_id}", status_code=204)
def delete_dealership(dealership_id: int, db: Session = Depends(get_db)):
    # Deletes the dealership; raises 404 if not found
    ok = Svc.delete(db, dealership_id)
    if not ok:
        raise HTTPException(404, "Dealership not found")
    return Response(status_code=204)

# ---- Exports ----

# Export all dealerships as JSON
@router.get("/_export/json")
def export_json(db: Session = Depends(get_db)):
    # Returns all dealerships in JSON format
    return JSONResponse(content=Svc.export_json(db))

# Export all dealerships as plain text
@router.get("/_export/txt")
def export_txt(db: Session = Depends(get_db)):
    # Returns all dealerships in plain text format
    return PlainTextResponse(content=Svc.export_txt(db), media_type="text/plain")