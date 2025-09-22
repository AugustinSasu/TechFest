# owner:POP MIRCEA STEFAN
# CRATE_DATE: 2024-06-20 10:40
# LAST MODIFY_DATE: --
# MODIFY BY: --


# Description: This module defines the API routes for managing customer entities.
# It includes endpoints for creating, retrieving, updating, deleting, and filtering customers.
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from typing import List, Optional
from sqlalchemy.orm import Session

from database.session import get_db
from schemas.customer import CustomerCreate, CustomerUpdate, CustomerOut
from services.customer_service import CustomerService


#the full route to the endpoint will be api/customers
router = APIRouter(prefix="/customers", tags=["customers"])
svc = CustomerService()

# Create a new customer
# Example request body:
# {
#   "full_name": "John Doe",
#   "phone": "123-456-7890",
#   "email": "
#   "address": "123 Main St, Anytown, USA"
# } ....
#]
@router.post("", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    return svc.create(db, payload)

# List customers with optional filtering, sorting, and pagination
# Example of call:
# /api/customers?full_name=John&sort=desc&skip=0&
#response example
# [
#   {
#     "customer_id": 1,
#     "full_name": "John Doe",
#     "phone": "123-456-7890",
#     "email": "email@gmail.com"
#     "address": "123 Main St, Anytown, USA"
#   },
@router.get("", response_model=List[CustomerOut])
def list_customers(
    full_name: Optional[str] = Query(None, description="Filtrare după nume (LIKE)"),
    sort: str = Query("asc", pattern="^(?i)(asc|desc)$", description="Sortare după customer_id: asc/desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, gt=0, le=1000),
    db: Session = Depends(get_db),
):
    return svc.list(db, full_name=full_name, sort=sort, skip=skip, limit=limit)

# Retrieve a customer by ID
# Example response body:
# {
#   "customer_id": 1,
#   "full_name": "John Doe",
#   "phone": "123-456-7890",
#   "email": "email@email.com",
#   "address": "123 Main St, Anytown, USA"
# }
@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(
    customer_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    obj = svc.get(db, customer_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Customer not found")
    return obj

# Update a customer by ID
# Example request body:
# {
#   "full_name": "Jane Doe",
#   "phone": "987-654-3210",
#   "email": "email@email.com",
#   "address": "456 Elm St, Othertown, USA"
# }
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
# Delete a customer by ID
# Example of call: DELETE /api/customers/1
# Response: 204 No Content
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

# Get customers by phone number
# Example of call: /api/customers/by-phone/123-456-7890
# Response example:
# [
#   {
#     "customer_id": 1,
#     "full_name": "John Doe",
#     "phone": "123-456-7890",
#     "email": "
#     "address": "123 Main St, Anytown, USA"
#   },
#   {
#     ...
#   }
# ]
@router.get("/by-phone/{phone}", response_model=List[CustomerOut])
def customers_by_phone(
    phone: str = Path(..., min_length=1),
    db: Session = Depends(get_db),
):
    return svc.by_phone(db, phone)

# Get customers by email address
# Example of call: /api/customers/by-email/email%40email.com
# (Note: email should be URL-encoded)
# Response example:
# [
#   {
#     "customer_id": 1,
#     "full_name": "John Doe",
#     "phone": "123-456-7890",
#     "email": "email@email.com",
#     "address": "123 Main St, Anytown, USA"
#   },
#   {
#     ...
#   }
@router.get("/by-email/{email}", response_model=List[CustomerOut])
def customers_by_email(
    email: str = Path(..., min_length=3),
    db: Session = Depends(get_db),
):
    # Dacă ai email-uri cu caractere speciale, URL-encode din client.
    return svc.by_email(db, email)
