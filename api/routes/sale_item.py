from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from database.session import get_db
from services.sale_item_service import SaleItemService
from schemas.sale_item import SaleItemCreate, SaleItemUpdate, SaleItemOut
from decimal import Decimal

router = APIRouter(prefix="/sale-items", tags=["sale-items"])

@router.get("/", response_model=List[SaleItemOut])
def list_sale_items(
    order_id: Optional[int] = Query(None),
    item_type: Optional[str] = Query(None, pattern="^(CAR|SERVICE)$"),
    sort: str = Query("asc", pattern="^(asc|desc)$"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    rows = SaleItemService.list(db, order_id, item_type, sort, limit, offset)
    return [
        SaleItemOut(
            item_id=r.item_id,
            order_id=r.order_id,
            item_type=r.item_type,
            vehicle_id=r.vehicle_id,
            service_id=r.service_id,
            qty=r.qty,
            unit_price=r.unit_price,
            line_total=SaleItemService.compute_line_total(Decimal(r.qty), Decimal(r.unit_price)),
        )
        for r in rows
    ]

@router.get("/{item_id}", response_model=SaleItemOut)
def get_sale_item(item_id: int, db: Session = Depends(get_db)):
    r = SaleItemService.get(db, item_id)
    if not r:
        raise HTTPException(status_code=404, detail="Sale item not found")
    return SaleItemOut(
        item_id=r.item_id, order_id=r.order_id, item_type=r.item_type,
        vehicle_id=r.vehicle_id, service_id=r.service_id, qty=r.qty, unit_price=r.unit_price,
        line_total=SaleItemService.compute_line_total(Decimal(r.qty), Decimal(r.unit_price)),
    )

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SaleItemOut)
def create_sale_item(payload: SaleItemCreate, db: Session = Depends(get_db)):
    try:
        r = SaleItemService.create(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return SaleItemOut(
        item_id=r.item_id, order_id=r.order_id, item_type=r.item_type,
        vehicle_id=r.vehicle_id, service_id=r.service_id, qty=r.qty, unit_price=r.unit_price,
        line_total=SaleItemService.compute_line_total(Decimal(r.qty), Decimal(r.unit_price)),
    )

@router.put("/{item_id}", response_model=SaleItemOut)
def update_sale_item(item_id: int, payload: SaleItemUpdate, db: Session = Depends(get_db)):
    r = SaleItemService.update(db, item_id, payload)
    if not r:
        raise HTTPException(status_code=404, detail="Sale item not found")
    return SaleItemOut(
        item_id=r.item_id, order_id=r.order_id, item_type=r.item_type,
        vehicle_id=r.vehicle_id, service_id=r.service_id, qty=r.qty, unit_price=r.unit_price,
        line_total=SaleItemService.compute_line_total(Decimal(r.qty), Decimal(r.unit_price)),
    )

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale_item(item_id: int, db: Session = Depends(get_db)):
    ok = SaleItemService.delete(db, item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Sale item not found")
    return
