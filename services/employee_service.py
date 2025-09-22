# owner:POP MIRCEA STEFAN
# CRATE_DATE: 2024-06-20 10:40
# LAST MODIFY_DATE: --
# MODIFY BY: --

# services/employee_service.py
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeRegister
from models.employee import Employee
from repositories.employee_repository import EmployeeRepository

class EmployeeService:
    def __init__(self, repo: EmployeeRepository | None = None):
        self.repo = repo or EmployeeRepository()

    # CRUD
    def create(self, db: Session, payload: EmployeeCreate) -> Employee:
        data = payload.model_dump()
        try:
            return self.repo.create(db, data=data)
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="db_username already exists")

    def register(self, db: Session, payload: EmployeeRegister) -> Employee:
        data = payload.model_dump()
        try:
            return self.repo.create(db, data=data)
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="db_username already exists")

    def get(self, db: Session, employee_id: int) -> Optional[Employee]:
        return self.repo.get(db, employee_id=employee_id)

    def update(self, db: Session, employee_id: int, payload: EmployeeUpdate) -> Optional[Employee]:
        data = {k: v for k, v in payload.model_dump().items() if v is not None}
        try:
            return self.repo.update(db, employee_id=employee_id, data=data)
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="db_username already exists")

    def delete(self, db: Session, employee_id: int) -> bool:
        return self.repo.delete(db, employee_id=employee_id)

    def list(
        self,
        db: Session,
        *,
        full_name: Optional[str],
        role_code: Optional[str],
        dealership_id: Optional[int],
        sort: str,
        skip: int,
        limit: int,
    ) -> List[Employee]:
        sort = sort.lower()
        if sort not in {"asc", "desc"}:
            sort = "asc"
        return self.repo.list(
            db,
            full_name=full_name,
            role_code=role_code,
            dealership_id=dealership_id,
            sort=sort,
            skip=skip,
            limit=limit,
        )

    # Sign-in simplu (fără token, parole în clar)
    def sign_in(self, db: Session, *, db_username: str, password: str) -> Optional[Employee]:
        user = self.repo.get_by_username(db, db_username=db_username)
        if not user or (user.password or "") != password:
            return None
        return user

    def get_by_username(self, db: Session, *, db_username: str) -> Optional[Employee]:
        return self.repo.get_by_username(db, db_username=db_username)
