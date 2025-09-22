# api/routes/car_sale_item.py

from typing import List, Optional, Iterable
import csv
from io import StringIO

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session

from database.session import get_db
from schemas.car_sale_item import CarSaleItemCreate, CarSaleItemUpdate, CarSaleItemOut
from services.car_sale_item_service import CarSaleItemService

router = APIRouter(prefix="/car-sale-items", tags=["car-sale-items"])
svc = CarSaleItemService()

#the full route to the endpoint will be api/car-sale-items
@router.post("", response_model=CarSaleItemOut, status_code=status.HTTP_201_CREATED)
def create_car_sale_item(payload: CarSaleItemCreate, db: Session = Depends(get_db)):
    return svc.create(db, payload)

@router.get("", response_model=List[CarSaleItemOut])
def list_car_sale_items(
    order_id: Optional[int] = Query(None, ge=1, description="Filtru după order_id"),
    min_price: Optional[float] = Query(None, ge=0, description="Preț minim (inclusiv)"),
    max_price: Optional[float] = Query(None, ge=0, description="Preț maxim (inclusiv)"),
    sort_by: str = Query("item_id", pattern="^(?i)(item_id|order_id)$", description="Câmp de sortare"),
    sort: str = Query("asc", pattern="^(?i)(asc|desc)$", description="Ordinea de sortare"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, gt=0, le=10000),
    db: Session = Depends(get_db),
):
    rows = svc.list(
        db,
        order_id=order_id,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        sort=sort,
        skip=skip,
        limit=limit,
    )
    return [CarSaleItemOut.model_validate(r) for r in rows]

@router.get("/{item_id}", response_model=CarSaleItemOut)
def get_car_sale_item(item_id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    obj = svc.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="CarSaleItem not found")
    return obj

@router.put("/{item_id}", response_model=CarSaleItemOut)
def update_car_sale_item(item_id: int, payload: CarSaleItemUpdate, db: Session = Depends(get_db)):
    obj = svc.update(db, item_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="CarSaleItem not found")
    return obj

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_car_sale_item(item_id: int, db: Session = Depends(get_db)):
    ok = svc.delete(db, item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="CarSaleItem not found")
    return None

# ---------- Export JSON ----------
@router.get("/export.json")
def export_car_sale_items_json(
    order_id: Optional[int] = Query(None, ge=1),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    sort_by: str = Query("item_id", pattern="^(?i)(item_id|order_id)$"),
    sort: str = Query("asc", pattern="^(?i)(asc|desc)$"),
    skip: int = 0,
    limit: int = 10000,
    db: Session = Depends(get_db),
):
    rows = svc.list(
        db, order_id=order_id, min_price=min_price, max_price=max_price,
        sort_by=sort_by, sort=sort, skip=skip, limit=limit
    )
    data = [CarSaleItemOut.model_validate(r).model_dump() for r in rows]
    headers = {"Content-Disposition": 'attachment; filename="car_sale_items.json"'}
    return JSONResponse(content=data, headers=headers)

# ---------- Export CSV ----------
@router.get("/export.csv")
def export_car_sale_items_csv(
    order_id: Optional[int] = Query(None, ge=1),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    sort_by: str = Query("item_id", pattern="^(?i)(item_id|order_id)$"),
    sort: str = Query("asc", pattern="^(?i)(asc|desc)$"),
    skip: int = 0,
    limit: int = 10000,
    db: Session = Depends(get_db),
):
    rows = svc.list(
        db, order_id=order_id, min_price=min_price, max_price=max_price,
        sort_by=sort_by, sort=sort, skip=skip, limit=limit
    )

    def iter_csv(items) -> Iterable[str]:
        f = StringIO()
        writer = csv.writer(f)
        writer.writerow(["item_id", "order_id", "vehicle_id", "unit_price"])
        yield f.getvalue(); f.seek(0); f.truncate(0)
        for r in items:
            writer.writerow([r.item_id, r.order_id, r.vehicle_id, f"{float(r.unit_price):.2f}"])
            yield f.getvalue(); f.seek(0); f.truncate(0)

    headers = {"Content-Disposition": 'attachment; filename="car_sale_items.csv"'}
    return StreamingResponse(iter_csv(rows), media_type="text/csv", headers=headers)
