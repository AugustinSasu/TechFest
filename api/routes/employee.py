# api/routes/employees.py
from typing import List, Optional, Iterable
import csv
from io import StringIO

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session

from database.session import get_db
from schemas.employee import (
    EmployeeCreate, EmployeeUpdate, EmployeeRegister,
    EmployeeOut, SignInRequest, SignInResponse
)
from services.employee_service import EmployeeService

router = APIRouter(prefix="/employees", tags=["employees"])
svc = EmployeeService()

# ---------- CRUD ----------
@router.post("", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db)):
    return svc.create(db, payload)

@router.get("", response_model=List[EmployeeOut])
def list_employees(
    full_name: Optional[str] = Query(None, description="Filtru LIKE după nume"),
    role_code: Optional[str] = Query(None, pattern="^(?i)(SALES|MANAGER)$"),
    dealership_id: Optional[int] = Query(None, ge=1),
    sort: str = Query("asc", pattern="^(?i)(asc|desc)$", description="Sortare după employee_id"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, gt=0, le=5000),
    db: Session = Depends(get_db),
):
    return svc.list(
        db,
        full_name=full_name,
        role_code=(role_code.upper() if role_code else None),
        dealership_id=dealership_id,
        sort=sort,
        skip=skip,
        limit=limit,
    )

@router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee(employee_id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    obj = svc.get(db, employee_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Employee not found")
    return obj

@router.put("/{employee_id}", response_model=EmployeeOut)
def update_employee(employee_id: int, payload: EmployeeUpdate, db: Session = Depends(get_db)):
    obj = svc.update(db, employee_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Employee not found")
    return obj

@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    ok = svc.delete(db, employee_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Employee not found")
    return None

# ---------- Export JSON / CSV ----------
@router.get("/export.json")
def export_employees_json(
    full_name: Optional[str] = None,
    role_code: Optional[str] = Query(None, pattern="^(?i)(SALES|MANAGER)$"),
    dealership_id: Optional[int] = None,
    sort: str = Query("asc", pattern="^(?i)(asc|desc)$"),
    skip: int = 0,
    limit: int = 10000,
    db: Session = Depends(get_db),
):
    rows = svc.list(
        db,
        full_name=full_name,
        role_code=(role_code.upper() if role_code else None),
        dealership_id=dealership_id,
        sort=sort, skip=skip, limit=limit,
    )
    data = [EmployeeOut.model_validate(r).model_dump() for r in rows]
    headers = {"Content-Disposition": 'attachment; filename="employees.json"'}
    return JSONResponse(content=data, headers=headers)

@router.get("/export.csv")
def export_employees_csv(
    full_name: Optional[str] = None,
    role_code: Optional[str] = Query(None, pattern="^(?i)(SALES|MANAGER)$"),
    dealership_id: Optional[int] = None,
    sort: str = Query("asc", pattern="^(?i)(asc|desc)$"),
    skip: int = 0,
    limit: int = 10000,
    db: Session = Depends(get_db),
):
    rows = svc.list(
        db,
        full_name=full_name,
        role_code=(role_code.upper() if role_code else None),
        dealership_id=dealership_id,
        sort=sort, skip=skip, limit=limit,
    )

    def iter_csv(items) -> Iterable[str]:
        f = StringIO()
        writer = csv.writer(f)
        writer.writerow(["employee_id","db_username","full_name","role_code","dealership_id"])
        yield f.getvalue(); f.seek(0); f.truncate(0)
        for r in items:
            writer.writerow([r.employee_id, r.db_username, r.full_name, r.role_code, r.dealership_id])
            yield f.getvalue(); f.seek(0); f.truncate(0)

    headers = {"Content-Disposition": 'attachment; filename="employees.csv"'}
    return StreamingResponse(iter_csv(rows), media_type="text/csv", headers=headers)

# ---------- Register / Sign-in (fără securitate) ----------
@router.post("/register", response_model=EmployeeOut, status_code=201)
def register_employee(payload: EmployeeRegister, db: Session = Depends(get_db)):
    return svc.register(db, payload)

@router.post("/sign-in", response_model=SignInResponse)
def sign_in(body: SignInRequest, db: Session = Depends(get_db)):
    user = svc.sign_in(db, db_username=body.db_username, password=body.password)
    if not user:
        # 401 simplu; alternativ poți întoarce 200 cu authenticated=false
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return SignInResponse(authenticated=True, employee=EmployeeOut.model_validate(user))
