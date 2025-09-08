from typing import List, Optional
from sqlalchemy.orm import Session
from schemas.customer import CustomerCreate, CustomerUpdate
from models.customer import Customer
from repositories.customer_repository import CustomerRepository

class CustomerService:
    def __init__(self, repo: CustomerRepository | None = None):
        self.repo = repo or CustomerRepository()

    def create(self, db: Session, payload: CustomerCreate) -> Customer:
        return self.repo.create(db, data=payload.model_dict())

    def get(self, db: Session, customer_id: int) -> Optional[Customer]:
        return self.repo.get(db, customer_id=customer_id)

    def update(self, db: Session, customer_id: int, payload: CustomerUpdate) -> Optional[Customer]:
        # filtrăm cheile None ca să permitem PATCH-like behavior
        data = {k: v for k, v in payload.model_dump().items() if v is not None}
        return self.repo.update(db, customer_id=customer_id, data=data)

    def delete(self, db: Session, customer_id: int) -> bool:
        return self.repo.delete(db, customer_id=customer_id)

    def list(self, db: Session, *, full_name: Optional[str], sort: str, skip: int, limit: int) -> List[Customer]:
        sort = sort.lower()
        if sort not in {"asc", "desc"}:
            sort = "asc"
        return self.repo.list(db, full_name=full_name, sort=sort, skip=skip, limit=limit)

    def by_phone(self, db: Session, phone: str) -> List[Customer]:
        return self.repo.by_phone(db, phone=phone)

    def by_email(self, db: Session, email: str) -> List[Customer]:
        return self.repo.by_email(db, email=email)
