# api/routes/review.py
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session

from database.session import get_db
from schemas.review import ReviewCreate, ReviewUpdate, ReviewOut
from services.review_service import ReviewService



#the full route to the endpoint will be api/reviews
router = APIRouter(prefix="/reviews", tags=["reviews"])
svc = ReviewService()

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

@router.get("", response_model=List[ReviewOut])
def list_reviews(
    salesperson_id: Optional[int] = Query(None, ge=1),
    manager_id: Optional[int] = Query(None, ge=1),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    q: Optional[str] = Query(None, description="Căutare în review_text"),
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

@router.get("/{review_id}", response_model=ReviewOut)
def get_review(review_id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    row = svc.get(db, review_id)
    if not row:
        raise HTTPException(status_code=404, detail="Review not found")
    return ReviewOut.model_validate(row)

@router.put("/{review_id}", response_model=ReviewOut)
def update_review(review_id: int, payload: ReviewUpdate, db: Session = Depends(get_db)):
    row = svc.update(db, review_id, payload)
    if not row:
        raise HTTPException(status_code=404, detail="Review not found")
    return ReviewOut.model_validate(row)

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(review_id: int, db: Session = Depends(get_db)):
    ok = svc.delete(db, review_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Review not found")
    return None


# ---------- Endpoint special: toate pentru un salesperson (cele mai noi primele) ----------
@router.get("/by-salesperson/{salesperson_id}", response_model=List[ReviewOut])
def list_reviews_by_salesperson(
    salesperson_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    rows = svc.list_by_salesperson(db, salesperson_id)
    return [ReviewOut.model_validate(r) for r in rows]
