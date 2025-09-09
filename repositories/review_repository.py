# repository/review_repository.py
from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import select, desc, asc

from models.review import Review


class ReviewRepository:
    # CREATE
    def create(self, db: Session, payload) -> Review:
        row = Review(
            manager_id=payload.manager_id,
            salesperson_id=payload.salesperson_id,
            review_text=payload.review_text,
            review_date=payload.review_date,  # poate fi None -> DB default
        )
        db.add(row)
        db.flush()  # ca să avem review_id + valori implicite
        db.refresh(row)
        return row

    # READ (one)
    def get(self, db: Session, review_id: int) -> Optional[Review]:
        return db.get(Review, review_id)

    # READ (list)
    def list(
        self,
        db: Session,
        *,
        salesperson_id: Optional[int] = None,
        manager_id: Optional[int] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        q: Optional[str] = None,
        sort_by: str = "review_date",
        sort: str = "desc",
        skip: int = 0,
        limit: int = 100,
    ) -> List[Review]:
        stmt = select(Review)

        if salesperson_id:
            stmt = stmt.where(Review.salesperson_id == salesperson_id)
        if manager_id:
            stmt = stmt.where(Review.manager_id == manager_id)
        if date_from:
            stmt = stmt.where(Review.review_date >= date_from)
        if date_to:
            stmt = stmt.where(Review.review_date <= date_to)
        if q:
            # filtrare simplă în text (case-insensitive pentru SQLite/Postgres)
            like = f"%{q}%"
            stmt = stmt.where(Review.review_text.ilike(like))  # pe Oracle, folosește LOWER()

        # sortare
        sortable = {
            "review_id": Review.review_id,
            "review_date": Review.review_date,
        }
        col = sortable.get(sort_by, Review.review_date)
        stmt = stmt.order_by(desc(col) if str(sort).lower() == "desc" else asc(col))

        stmt = stmt.offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    # LIST by salesperson (desc by date)
    def list_by_salesperson(self, db: Session, salesperson_id: int) -> List[Review]:
        stmt = (
            select(Review)
            .where(Review.salesperson_id == salesperson_id)
            .order_by(desc(Review.review_date), desc(Review.review_id))
        )
        return list(db.execute(stmt).scalars().all())

    # UPDATE
    def update(self, db: Session, review_id: int, payload) -> Optional[Review]:
        row = db.get(Review, review_id)
        if not row:
            return None
        if payload.manager_id is not None:
            row.manager_id = payload.manager_id
        if payload.salesperson_id is not None:
            row.salesperson_id = payload.salesperson_id
        if payload.review_text is not None:
            row.review_text = payload.review_text
        if payload.review_date is not None:
            row.review_date = payload.review_date
        db.flush()
        db.refresh(row)
        return row

    # DELETE
    def delete(self, db: Session, review_id: int) -> bool:
        row = db.get(Review, review_id)
        if not row:
            return False
        db.delete(row)
        db.flush()
        return True
