# owner:POP MIRCEA STEFAN
# CRATE_DATE: 2024-06-20 10:40
# LAST MODIFY_DATE: --
# MODIFY BY: --
# services/review_service.py
from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session

from repositories.review_repository import ReviewRepository
from schemas.review import ReviewCreate, ReviewUpdate
from models.review import Review


class ReviewService:
    def __init__(self):
        self.repo = ReviewRepository()

    # CREATE
    def create(self, db: Session, payload: ReviewCreate) -> Review:
        # ne bazăm pe FK pentru a valida existența manager/salesperson
        return self.repo.create(db, payload)

    # READ
    def get(self, db: Session, review_id: int) -> Optional[Review]:
        return self.repo.get(db, review_id)

    # LIST
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
        return self.repo.list(
            db,
            salesperson_id=salesperson_id,
            manager_id=manager_id,
            date_from=date_from,
            date_to=date_to,
            q=q,
            sort_by=sort_by,
            sort=sort,
            skip=skip,
            limit=limit,
        )

    # LIST by salesperson (desc by date)
    def list_by_salesperson(self, db: Session, salesperson_id: int) -> List[Review]:
        return self.repo.list_by_salesperson(db, salesperson_id)

    # UPDATE
    def update(self, db: Session, review_id: int, payload: ReviewUpdate) -> Optional[Review]:
        return self.repo.update(db, review_id, payload)

    # DELETE
    def delete(self, db: Session, review_id: int) -> bool:
        return self.repo.delete(db, review_id)
