from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from typing import List, Optional
from sqlalchemy.orm import Session

from database.session import get_db
from schemas.customer import CustomerCreate, CustomerUpdate, CustomerOut
from services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["customers"])
svc = CustomerService()

@router.post("", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    return svc.create(db, payload)

@router.get("", response_model=List[CustomerOut])
def list_customers(
    full_name: Optional[str] = Query(None, description="Filtrare după nume (LIKE)"),
    sort: str = Query("asc", pattern="^(?i)(asc|desc)$", description="Sortare după customer_id: asc/desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, gt=0, le=1000),
    db: Session = Depends(get_db),
):
    return svc.list(db, full_name=full_name, sort=sort, skip=skip, limit=limit)

@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(
    customer_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    obj = svc.get(db, customer_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Customer not found")
    return obj

@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
):
    obj = svc.update(db, customer_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Customer not found")
    return obj

@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
):
    ok = svc.delete(db, customer_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Customer not found")
    return None

# ------- filtre prin PATH, conform cerinței tale -------
@router.get("/by-phone/{phone}", response_model=List[CustomerOut])
def customers_by_phone(
    phone: str = Path(..., min_length=1),
    db: Session = Depends(get_db),
):
    return svc.by_phone(db, phone)

@router.get("/by-email/{email}", response_model=List[CustomerOut])
def customers_by_email(
    email: str = Path(..., min_length=3),
    db: Session = Depends(get_db),
):
    # Dacă ai email-uri cu caractere speciale, URL-encode din client.
    return svc.by_email(db, email)
