from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, asc
from models.customer import Customer

class CustomerRepository:
    def create(self, db: Session, *, data: dict) -> Customer:
        obj = Customer(**data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def get(self, db: Session, *, customer_id: int) -> Optional[Customer]:
        return db.get(Customer, customer_id)

    def delete(self, db: Session, *, customer_id: int) -> bool:
        obj = self.get(db, customer_id=customer_id)
        if not obj:
            return False
        db.delete(obj)
        db.commit()
        return True

    def update(self, db: Session, *, customer_id: int, data: dict) -> Optional[Customer]:
        obj = self.get(db, customer_id=customer_id)
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
        return obj

    def list(
        self,
        db: Session,
        *,
        full_name: Optional[str] = None,
        sort: str = "asc",
        skip: int = 0,
        limit: int = 100,
    ) -> List[Customer]:
        stmt = select(Customer)
        if full_name:
            # match simplu: LIKE '%full_name%'
            stmt = stmt.where(Customer.full_name.ilike(f"%{full_name}%"))
        order_col = asc(Customer.customer_id) if sort.lower() != "desc" else desc(Customer.customer_id)
        stmt = stmt.order_by(order_col).offset(skip).limit(limit)
        return list(db.scalars(stmt))

    def by_phone(self, db: Session, *, phone: str) -> List[Customer]:
        stmt = select(Customer).where(Customer.phone == phone)
        return list(db.scalars(stmt))

    def by_email(self, db: Session, *, email: str) -> List[Customer]:
        stmt = select(Customer).where(Customer.email == email)
        return list(db.scalars(stmt))
