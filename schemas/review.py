# schemas/review.py
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ReviewBase(BaseModel):
    manager_id: int = Field(..., ge=1)
    salesperson_id: int = Field(..., ge=1)
    review_text: str = Field(..., min_length=1, max_length=10000)
    review_date: Optional[date] = Field(None, description="Dacă lipsește, DB pune CURRENT_DATE")

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    manager_id: Optional[int] = Field(None, ge=1)
    salesperson_id: Optional[int] = Field(None, ge=1)
    review_text: Optional[str] = Field(None, min_length=1, max_length=10000)
    review_date: Optional[date] = None

class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    review_id: int
    manager_id: int
    salesperson_id: int
    review_date: date
    review_text: str
