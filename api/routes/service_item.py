# ------------------------------------------------------------------

# Acest fișier definește toate endpointurile FastAPI pentru entitatea `service_item`.
# Fiecare rută apelează `ServiceItemService` și folosește `schemas.service_item` pentru validare input/output.

# Autor: Cristian-Valentin Alexa
# Data: 14 Aprilie 2024

# ------------------------------------------------------------------


from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database.session import get_db
from services.service_item_service import ServiceItemService
from schemas.service_item import ServiceItemCreate, ServiceItemUpdate, ServiceItemOut
#the full route to the endpoint will be api/service-items
router = APIRouter(prefix="/service-items", tags=["service-items"])

@router.get("/", response_model=List[ServiceItemOut])
def list_service_items(
    q: Optional[str] = Query(None, description="Caută în numele serviciului"),
    service_type: Optional[str] = Query(None, description="Filtru: CASCO, EXTRA_OPTION, etc."),
    sort: str = Query("asc", pattern="^(asc|desc)$"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Returnează toate serviciile definite, cu filtre opționale (text, tip) și paginare.
    """
    return ServiceItemService.list(db, q, service_type, sort, limit, offset)

@router.get("/{service_id}", response_model=ServiceItemOut)
def get_service_item(service_id: int, db: Session = Depends(get_db)):
    """
    Returnează un serviciu specific după ID.
    """
    obj = ServiceItemService.get(db, service_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Service item not found")
    return obj

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ServiceItemOut)
def create_service_item(payload: ServiceItemCreate, db: Session = Depends(get_db)):
    """
    Creează un nou serviciu (CASCO, garanție, etc).
    """
    return ServiceItemService.create(db, payload)

@router.put("/{service_id}", response_model=ServiceItemOut)
def update_service_item(service_id: int, payload: ServiceItemUpdate, db: Session = Depends(get_db)):
    """
    Actualizează serviciul existent.
    """
    obj = ServiceItemService.update(db, service_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Service item not found")
    return obj

@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service_item(service_id: int, db: Session = Depends(get_db)):
    """
    Șterge un serviciu din baza de date.
    """
    ok = ServiceItemService.delete(db, service_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Service item not found")
    return

@router.get("/export/json", response_model=List[dict])
def export_service_items_json(db: Session = Depends(get_db)):
    """
    Exportă toate serviciile ca listă JSON.
    """
    return ServiceItemService.export_json(db)

@router.get("/export/txt", response_model=str)
def export_service_items_txt(db: Session = Depends(get_db)):
    """
    Exportă serviciile sub formă de text tabelar (.txt).
    """
    return ServiceItemService.export_txt(db)
