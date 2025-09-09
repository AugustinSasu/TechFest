# api/routes/service_sale_item.py
# service_sale_item.py
# --------------------------------------

# Definește toate endpointurile FastAPI pentru entitatea `service_sale_item`.
# Expune API REST complet: CRUD + listare + export JSON / TXT

# Autor: Cristian-Valentin Alexa
# Data: 14 Aprilie 2024

# ---------------------------------------------------------------

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from decimal import Decimal

from database.session import get_db
from services.service_sale_item_service import ServiceSaleItemService
from schemas.service_sale_item import ServiceSaleItemCreate, ServiceSaleItemUpdate, ServiceSaleItemOut
from schemas.sale_order import SaleOrderOut
from services.sale_order_service import SaleOrderService

router = APIRouter(prefix="/service-sale-items", tags=["service-sale-items"])

@router.get("/", response_model=List[ServiceSaleItemOut])
def list_service_sale_items(
    order_id: Optional[int] = Query(None, description="Filtru: ID-ul comenzii"),
    service_id: Optional[int] = Query(None, description="Filtru: ID-ul serviciului"),
    sort: str = Query("asc", pattern="^(asc|desc)$"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    rows = ServiceSaleItemService.list(db, order_id, service_id, sort, limit, offset)
    return [
        ServiceSaleItemOut(
            item_id=r.item_id,
            order_id=r.order_id,
            service_id=r.service_id,
            qty=r.qty,
            unit_price=r.unit_price,
            line_total=ServiceSaleItemService.compute_line_total(r.qty, r.unit_price)
        ) for r in rows
    ]

@router.get("/{item_id}", response_model=ServiceSaleItemOut)
def get_service_sale_item(item_id: int, db: Session = Depends(get_db)):
    r = ServiceSaleItemService.get(db, item_id)
    if not r:
        raise HTTPException(status_code=404, detail="Service sale item not found")
    return ServiceSaleItemOut(
        item_id=r.item_id,
        order_id=r.order_id,
        service_id=r.service_id,
        qty=r.qty,
        unit_price=r.unit_price,
        line_total=ServiceSaleItemService.compute_line_total(r.qty, r.unit_price)
    )

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ServiceSaleItemOut)
def create_service_sale_item(payload: ServiceSaleItemCreate, db: Session = Depends(get_db)):
    r = ServiceSaleItemService.create(db, payload)
    return ServiceSaleItemOut(
        item_id=r.item_id,
        order_id=r.order_id,
        service_id=r.service_id,
        qty=r.qty,
        unit_price=r.unit_price,
        line_total=ServiceSaleItemService.compute_line_total(r.qty, r.unit_price)
    )

@router.put("/{item_id}", response_model=ServiceSaleItemOut)
def update_service_sale_item(item_id: int, payload: ServiceSaleItemUpdate, db: Session = Depends(get_db)):
    r = ServiceSaleItemService.update(db, item_id, payload)
    if not r:
        raise HTTPException(status_code=404, detail="Service sale item not found")
    return ServiceSaleItemOut(
        item_id=r.item_id,
        order_id=r.order_id,
        service_id=r.service_id,
        qty=r.qty,
        unit_price=r.unit_price,
        line_total=ServiceSaleItemService.compute_line_total(r.qty, r.unit_price)
    )

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service_sale_item(item_id: int, db: Session = Depends(get_db)):
    ok = ServiceSaleItemService.delete(db, item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Service sale item not found")
    return

@router.get("/export/json", response_model=List[dict])
def export_service_sale_items_json(db: Session = Depends(get_db)):
    return ServiceSaleItemService.export_json(db)

@router.get("/export/txt", response_model=str)
def export_service_sale_items_txt(db: Session = Depends(get_db)):
    return ServiceSaleItemService.export_txt(db)

@router.get("/by-employee/{employee_id}", response_model=List[SaleOrderOut])
def get_orders_by_employee(employee_id: int, db: Session = Depends(get_db)):
    return SaleOrderService.list_by_salesperson(db, employee_id)
