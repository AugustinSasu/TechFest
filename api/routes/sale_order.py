# api/routes/sale_order.py
# ROUTES: sale_order.py

# ---------------------------
# Endpointuri REST pentru entitatea `sale_order` (comandă de vânzare auto).
# Expune CRUD, listare filtrabilă și validări de status / client.

# Autor: Alexa Cristian-Valentin
# Data: 09-09-2024

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from database.session import get_db
from services.sale_order_service import SaleOrderService
from schemas.sale_order import SaleOrderCreate, SaleOrderUpdate, SaleOrderOut

router = APIRouter(prefix="/sale-orders", tags=["sale-orders"])

@router.get("/", response_model=List[SaleOrderOut])
def list_sale_orders(
    status: Optional[str] = Query(None, description="Status: OPEN, APPROVED etc."),
    customer_id: Optional[int] = Query(None),
    sort: str = Query("asc", pattern="^(asc|desc)$"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return SaleOrderService.list(db, status, customer_id, sort, limit, offset)

@router.get("/{order_id}", response_model=SaleOrderOut)
def get_sale_order(order_id: int, db: Session = Depends(get_db)):
    order = SaleOrderService.get(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Sale order not found")
    return order

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SaleOrderOut)
def create_sale_order(payload: SaleOrderCreate, db: Session = Depends(get_db)):
    return SaleOrderService.create(db, payload)

@router.put("/{order_id}", response_model=SaleOrderOut)
def update_sale_order(order_id: int, payload: SaleOrderUpdate, db: Session = Depends(get_db)):
    order = SaleOrderService.update(db, order_id, payload)
    if not order:
        raise HTTPException(status_code=404, detail="Sale order not found")
    return order

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale_order(order_id: int, db: Session = Depends(get_db)):
    ok = SaleOrderService.delete(db, order_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Sale order not found")
    return
