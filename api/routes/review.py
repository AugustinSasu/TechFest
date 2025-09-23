# api/routes/review.py
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session

from database.session import get_db
from schemas.review import ReviewCreate, ReviewUpdate, ReviewOut
from services.review_service import ReviewService

# Base router for "reviews" entity
# All endpoints will be available under /reviews
router = APIRouter(prefix="/reviews", tags=["reviews"])
svc = ReviewService()


# ---------------- CREATE ----------------
# POST /reviews
# Creates a new review.
# Example request:
#   POST /reviews
#   {
#     "salesperson_id": 7,
#     "manager_id": 3,
#     "review_date": "2025-09-01",
#     "review_text": "Reached Q3 target, excellent communication.",
#     "rating": 5
#   }
# Example response (201 Created):
#   {
#     "review_id": 101,
#     "salesperson_id": 7,
#     "manager_id": 3,
#     "review_date": "2025-09-01",
#     "review_text": "Reached Q3 target, excellent communication.",
#     "rating": 5
#   }
@router.post("", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(payload: ReviewCreate, db: Session = Depends(get_db)):
    try:
        row = svc.create(db, payload)
        db.flush()
        db.commit()
        db.refresh(row)
        return ReviewOut.model_validate(row)
    except Exception:
        db.rollback()
        raise


# ---------------- LIST ----------------
# GET /reviews
# Lists all reviews with optional filters and sorting.
# Filters:
#   - salesperson_id, manager_id
#   - date_from, date_to
#   - q (text search in review_text)
#   - skip, limit (pagination)
# Sorting:
#   - sort_by: review_date or review_id
#   - sort: asc or desc
# Example request:
#   GET /reviews?salesperson_id=7&date_from=2025-09-01&date_to=2025-09-30
# Example response (200 OK):
#   [
#     {
#       "review_id": 101,
#       "salesperson_id": 7,
#       "manager_id": 3,
#       "review_date": "2025-09-01",
#       "review_text": "Reached Q3 target, excellent communication.",
#       "rating": 5
#     },
#     {
#       "review_id": 99,
#       "salesperson_id": 7,
#       "manager_id": 3,
#       "review_date": "2025-08-15",
#       "review_text": "Good progress on ACME account.",
#       "rating": 4
#     }
#   ]
@router.get("", response_model=List[ReviewOut])
def list_reviews(
    salesperson_id: Optional[int] = Query(None, ge=1),
    manager_id: Optional[int] = Query(None, ge=1),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    q: Optional[str] = Query(None, description="Search in review_text"),
    sort_by: str = Query("review_date", pattern="^(?i)(review_date|review_id)$"),
    sort: str = Query("desc", pattern="^(?i)(asc|desc)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, gt=0, le=10000),
    db: Session = Depends(get_db),
):
    rows = svc.list(
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
    return [ReviewOut.model_validate(r) for r in rows]


# ---------------- GET BY ID ----------------
# GET /reviews/{review_id}
# Retrieves a single review by its ID.
# Example request:
#   GET /reviews/101
# Example response (200 OK):
#   {
#     "review_id": 101,
#     "salesperson_id": 7,
#     "manager_id": 3,
#     "review_date": "2025-09-01",
#     "review_text": "Reached Q3 target, excellent communication.",
#     "rating": 5
#   }
# Example response (404 Not Found):
#   {"detail": "Review not found"}
@router.get("/{review_id}", response_model=ReviewOut)
def get_review(review_id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    row = svc.get(db, review_id)
    if not row:
        raise HTTPException(status_code=404, detail="Review not found")
    return ReviewOut.model_validate(row)


# ---------------- UPDATE ----------------
# PUT /reviews/{review_id}
# Updates an existing review.
# Example request:
#   PUT /reviews/101
#   {
#     "review_date": "2025-09-02",
#     "review_text": "Updated feedback after client call.",
#     "rating": 4
#   }
# Example response (200 OK):
#   {
#     "review_id": 101,
#     "salesperson_id": 7,
#     "manager_id": 3,
#     "review_date": "2025-09-02",
#     "review_text": "Updated feedback after client call.",
#     "rating": 4
#   }
# Example response (404 Not Found):
#   {"detail": "Review not found"}
@router.put("/{review_id}", response_model=ReviewOut)
def update_review(review_id: int, payload: ReviewUpdate, db: Session = Depends(get_db)):
    row = svc.update(db, review_id, payload)
    if not row:
        raise HTTPException(status_code=404, detail="Review not found")
    return ReviewOut.model_validate(row)


# ---------------- DELETE ----------------
# DELETE /reviews/{review_id}
# Deletes a review by ID.
# Example request:
#   DELETE /reviews/101
# Example response (204 No Content):
#   (no content)
# Example response (404 Not Found):
#   {"detail": "Review not found"}
@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(review_id: int, db: Session = Depends(get_db)):
    ok = svc.delete(db, review_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Review not found")
    return None


# ---------------- LIST BY SALESPERSON ----------------
# GET /reviews/by-salesperson/{salesperson_id}
# Lists all reviews for a given salesperson, newest first.
# Example request:
#   GET /reviews/by-salesperson/7
# Example response (200 OK):
#   [
#     {
#       "review_id": 101,
#       "salesperson_id": 7,
#       "manager_id": 3,
#       "review_date": "2025-09-01",
#       "review_text": "Reached Q3 target, excellent communication.",
#       "rating": 5
#     }
#   ]
@router.get("/by-salesperson/{salesperson_id}", response_model=List[ReviewOut])
def list_reviews_by_salesperson(
    salesperson_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    rows = svc.list_by_salesperson(db, salesperson_id)
    return [ReviewOut.model_validate(r) for r in rows]
