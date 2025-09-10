# api/routes/sale_order.py
# ROUTES: sale_order.py
from datetime import date
# ---------------------------
# Endpointuri REST pentru entitatea `sale_order` (comandă de vânzare auto).
# Expune CRUD, listare filtrabilă și validări de status / client.

# Autor: Alexa Cristian-Valentin
# Data: 09-09-2024

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from database.session import get_db
from schemas.sale_stats import SalesOrderStatOut
from services.sale_order_service import SaleOrderService
from schemas.sale_order import SaleOrderCreate, SaleOrderUpdate, SaleOrderOut

def _norm_date(val: Optional[str], name: str) -> Optional[date]:
    if val is None or val == "":
        return None
    try:
        y, m, d = val.split("-")
        return date(int(y), int(m), int(d))
    except Exception:
        raise HTTPException(status_code=400, detail=f"{name} trebuie să fie în format YYYY-MM-DD")

# --- helper fallback pt. rezultate (mappings() vs fetchall())
def _first_mapping(res):
    try:
        return res.mappings().first()
    except AttributeError:
        row = res.fetchone()
        if row is None:
            return {}
        keys = res.keys()
        return dict(zip(keys, row))

def _all_mappings(res):
    try:
        return res.mappings().all()
    except AttributeError:
        rows = res.fetchall()
        keys = res.keys()
        return [dict(zip(keys, r)) for r in rows]

router = APIRouter(prefix="/sale-orders", tags=["sale-orders"])

@router.get("/stats", response_model=List[SalesOrderStatOut])
def list_sales_order_details(db: Session = Depends(get_db)):
    """
    Returnează lista detaliată a comenzilor (mașini + servicii), pe linii,
    sub formă de JSON tipat (Pydantic).
    """
    sql = text("""
        SELECT 
            so.order_id           AS sale_id,
            e.full_name           AS agent,
            d.name                AS nume_locatie,
            v.model               AS produs,
            csi.unit_price        AS pret,
            so.order_date         AS data_vanzare,
            d.region              AS regiune
        FROM sale_order so
        JOIN employee e        ON so.salesperson_id = e.employee_id
        JOIN dealership d      ON so.dealership_id = d.dealership_id
        JOIN car_sale_item csi ON so.order_id = csi.order_id
        JOIN vehicle v         ON csi.vehicle_id = v.vehicle_id

        UNION ALL

        SELECT 
            so.order_id           AS sale_id,
            e.full_name           AS agent,
            d.name                AS nume_locatie,
            s.name                AS produs,
            ssi.unit_price        AS pret,
            so.order_date         AS data_vanzare,
            d.region              AS regiune
        FROM sale_order so
        JOIN employee e         ON so.salesperson_id = e.employee_id
        JOIN dealership d       ON so.dealership_id = d.dealership_id
        JOIN service_sale_item ssi ON so.order_id = ssi.order_id
        JOIN service_item s     ON ssi.service_id = s.service_id
        ORDER BY sale_id
    """)

    # SQLAlchemy 1.4+/2.0: mappings() -> dict-like rows
    result = db.execute(sql).mappings().all()
    return [dict(row) for row in result]






@router.get("/trends")
def sales_orders_trends(
    start_date_s: Optional[str] = Query(None, alias="start-date", description="Data de început (YYYY-MM-DD) inclusiv"),
    end_date_s:   Optional[str] = Query(None, alias="end-date",   description="Data de sfârșit (YYYY-MM-DD) inclusiv"),
    granulatie: int = Query(2, ge=1, le=3, description="1=săptămână (ISO), 2=lună, 3=an"),
    db: Session = Depends(get_db),
):
    """
        Returnează:
          - venit: suma totală încasată (doar comenzi INVOICED)
          - vanzari_incheiate: numărul de comenzi INVOICED
          - trend_vanzari: listă agregată după granulație (săptămână/lună/an) cu sumele încasate
        Filtrarea temporală se aplică pe so.order_date (capete incluse).

        **Cum se apelează (exemple)**

        Browser:
          • /api/sale-orders/trends?granulatie=2
          • /api/sale-orders/trends?start-date=2025-01-01&end-date=2025-12-31&granulatie=1
          • /api/sale-orders/trends?start-date=2022-01-01&end-date=2025-12-31&granulatie=3
            /api/sale-orders/trends?start-date=2025-01-01&end-date=2025-12-31&granulatie=1"

          - start-date: string (YYYY-MM-DD), opțional
          - end-date:   string (YYYY-MM-DD), opțional
          - granulatie: int {1=săptămână, 2=lună, 3=an}, obligatoriu

        Notă:
          - Sunt luate în calcul doar comenzile cu status 'INVOICED'.
          - Endpointul acceptă și date fără zero-padding (ex. 2025-12-3).
        """
    # Normalizăm datele să nu mai dea 422 (ex. 2025-12-3 devine 2025-12-03)
    start_date = _norm_date(start_date_s, "start-date")
    end_date   = _norm_date(end_date_s,   "end-date")

    if granulatie not in (1, 2, 3):
        raise HTTPException(status_code=400, detail="granulatie trebuie să fie 1 (săptămână), 2 (lună) sau 3 (an).")

    # Filtre data + status
    date_filters = ["so.status = 'INVOICED'"]
    params = {}
    if start_date:
        date_filters.append("TRUNC(so.order_date) >= :start_date")
        params["start_date"] = start_date
    if end_date:
        date_filters.append("TRUNC(so.order_date) <= :end_date")
        params["end_date"] = end_date

    where_clause = " AND ".join(date_filters)

    # 1) VENIT total (din mașini + servicii)
    sql_revenue = text(f"""
        WITH items AS (
            SELECT so.order_id, so.order_date, csi.unit_price AS amount
            FROM sale_order so
            JOIN car_sale_item csi ON csi.order_id = so.order_id
            WHERE {where_clause}
            UNION ALL
            SELECT so.order_id, so.order_date, (ssi.qty * ssi.unit_price) AS amount
            FROM sale_order so
            JOIN service_sale_item ssi ON ssi.order_id = so.order_id
            WHERE {where_clause}
        )
        SELECT NVL(SUM(amount), 0) AS venit
        FROM items
    """)
    venit_row = _first_mapping(db.execute(sql_revenue, params))
    venit_val = float((venit_row or {}).get("VENIT", 0) or (venit_row or {}).get("venit", 0) or 0)

    # 2) VÂNZĂRI ÎNCHEIATE (număr comenzi INVOICED)
    sql_closed = text(f"""
        SELECT COUNT(*) AS cnt
        FROM sale_order so
        WHERE {where_clause}
    """)
    closed_row = _first_mapping(db.execute(sql_closed, params))
    vanzari_incheiate_val = int((closed_row or {}).get("CNT", 0) or (closed_row or {}).get("cnt", 0) or 0)

    # 3) TREND după granularitate
    if granulatie == 1:
        trunc_mask = "IW"
        label_expr = "TO_CHAR(TRUNC(order_date, 'IW'), 'IYYY-IW')"   # ISO Week (IYYY-IW)
        label_key = "nr_saptamana"
    elif granulatie == 2:
        trunc_mask = "MM"
        label_expr = "TO_CHAR(TRUNC(order_date, 'MM'), 'YYYY-MM')"   # Lună
        label_key = "luna_an"
    else:
        trunc_mask = "YYYY"
        label_expr = "TO_CHAR(TRUNC(order_date, 'YYYY'), 'YYYY')"    # An
        label_key = "an"

    sql_trend = text(f"""
        WITH items AS (
            SELECT so.order_id, so.order_date, csi.unit_price AS amount
            FROM sale_order so
            JOIN car_sale_item csi ON csi.order_id = so.order_id
            WHERE {where_clause}
            UNION ALL
            SELECT so.order_id, so.order_date, (ssi.qty * ssi.unit_price) AS amount
            FROM sale_order so
            JOIN service_sale_item ssi ON ssi.order_id = so.order_id
            WHERE {where_clause}
        )
        SELECT 
            {label_expr} AS label,
            TRUNC(order_date, '{trunc_mask}') AS bucket_date,
            SUM(amount) AS suma
        FROM items
        GROUP BY TRUNC(order_date, '{trunc_mask}'), {label_expr}
        ORDER BY bucket_date
    """)
    trend_rows = _all_mappings(db.execute(sql_trend, params))

    def g(d, k):
        return d.get(k) or d.get(k.upper()) or d.get(k.lower())

    trend_vanzari = [
        {label_key: g(r, "label"), "suma_incasata": float(g(r, "suma") or 0)}
        for r in trend_rows
    ]

    return {
        "venit": venit_val,
        "vanzari_incheiate": vanzari_incheiate_val,
        "trend_vanzari": trend_vanzari,
        "granulatie": granulatie,
        "interval": {
            "start_date": str(start_date) if start_date else None,
            "end_date": str(end_date) if end_date else None,
        },
    }
















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


# 🔄 Nou: returnează toate comenzile pentru un agent
@router.get("/by-employee/{employee_id}", response_model=List[SaleOrderOut])
def get_orders_by_employee(employee_id: int, db: Session = Depends(get_db)):
    return SaleOrderService.list_by_salesperson(db, employee_id)


# 

# 🔄 Endpoint: /sale-orders/filter?start-date=...&end-date=...&employee_id=...
@router.get("/filter", response_model=List[SaleOrderOut])
def filter_sale_orders_by_date(
    start_date_s: Optional[str] = Query(None, alias="start-date"),
    end_date_s: Optional[str] = Query(None, alias="end-date"),
    employee_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Returnează comenzile de vânzare dintr-un interval dat, opțional filtrate după `employee_id`.
    Exemplu:
      /api/sale-orders/filter?start-date=2023-01-01&end-date=2023-12-31
      /api/sale-orders/filter?start-date=2023-01-01&end-date=2023-12-31&employee_id=5
    """
    start_date = _norm_date(start_date_s, "start-date")
    end_date = _norm_date(end_date_s, "end-date")

    stmt = text("""
        SELECT * FROM sale_order
        WHERE (:start IS NULL OR TRUNC(order_date) >= :start)
          AND (:end IS NULL OR TRUNC(order_date) <= :end)
          AND (:emp IS NULL OR salesperson_id = :emp)
        ORDER BY order_date DESC
    """)
    params = {"start": start_date, "end": end_date, "emp": employee_id}
    rows = db.execute(stmt, params).mappings().all()
    return [SaleOrderOut(**row) for row in rows]
