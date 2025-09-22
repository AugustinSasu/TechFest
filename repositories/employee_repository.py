# owner:ALEXA VALENTIN
# CRATE_DATE: 2024-06-20 10:40
# LAST MODIFY_DATE: --
# MODIFY BY: --
# repositories/employee_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, asc, desc
from sqlalchemy.exc import IntegrityError
from models.employee import Employee

class EmployeeRepository:
    def create(self, db: Session, *, data: dict) -> Employee:
        obj = Employee(**data)
        db.add(obj)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise
        db.refresh(obj)
        return obj

    def get(self, db: Session, *, employee_id: int) -> Optional[Employee]:
        return db.get(Employee, employee_id)

    def get_by_username(self, db: Session, *, db_username: str) -> Optional[Employee]:
        stmt = select(Employee).where(Employee.db_username == db_username)
        return db.scalar(stmt)

    def update(self, db: Session, *, employee_id: int, data: dict) -> Optional[Employee]:
        obj = self.get(db, employee_id=employee_id)
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise
        db.refresh(obj)
        return obj

    def delete(self, db: Session, *, employee_id: int) -> bool:
        obj = self.get(db, employee_id=employee_id)
        if not obj:
            return False
        db.delete(obj)
        db.commit()
        return True

    def list(
        self,
        db: Session,
        *,
        full_name: Optional[str] = None,
        role_code: Optional[str] = None,
        dealership_id: Optional[int] = None,
        sort: str = "asc",
        skip: int = 0,
        limit: int = 100,
    ) -> List[Employee]:
        stmt = select(Employee)
        if full_name:
            stmt = stmt.where(Employee.full_name.ilike(f"%{full_name}%"))
        if role_code:
            stmt = stmt.where(Employee.role_code == role_code)
        if dealership_id:
            stmt = stmt.where(Employee.dealership_id == dealership_id)
        order_col = asc(Employee.employee_id) if sort.lower() != "desc" else desc(Employee.employee_id)
        stmt = stmt.order_by(order_col).offset(skip).limit(limit)
        return list(db.scalars(stmt))
