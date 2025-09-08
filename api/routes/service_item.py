from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from database.session import get_db
from services.service_item_service import ServiceItemService
from schemas.service_item import ServiceItemCreate, ServiceItemUpdate, ServiceItemOut

router = APIRouter(prefix="/service-items", tags=["service-items"])

@router.get("/", response_model=List[ServiceItemOut])
def list_service_items(
    q: Optional[str] = Query(None),
    service_type: Optional[str] = Query(None),
    sort: str = Query("asc", pattern="^(asc|desc)$"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    rows = ServiceItemService.list(db, q, service_type, sort, limit, offset)
    return [ServiceItemOut(service_id=r.service_id, service_type=r.service_type, name=r.name,
                           description=r.description, list_price=r.list_price) for r in rows]

@router.get("/{service_id}", response_model=ServiceItemOut)
def get_service_item(service_id: int, db: Session = Depends(get_db)):
    obj = ServiceItemService.get(db, service_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Service item not found")
    return ServiceItemOut(service_id=obj.service_id, service_type=obj.service_type,
                          name=obj.name, description=obj.description, list_price=obj.list_price)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ServiceItemOut)
def create_service_item(payload: ServiceItemCreate, db: Session = Depends(get_db)):
    obj = ServiceItemService.create(db, payload)
    return ServiceItemOut(service_id=obj.service_id, service_type=obj.service_type,
                          name=obj.name, description=obj.description, list_price=obj.list_price)

@router.put("/{service_id}", response_model=ServiceItemOut)
def update_service_item(service_id: int, payload: ServiceItemUpdate, db: Session = Depends(get_db)):
    obj = ServiceItemService.update(db, service_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Service item not found")
    return ServiceItemOut(service_id=obj.service_id, service_type=obj.service_type,
                          name=obj.name, description=obj.description, list_price=obj.list_price)

@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service_item(service_id: int, db: Session = Depends(get_db)):
    ok = ServiceItemService.delete(db, service_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Service item not found")
    return
