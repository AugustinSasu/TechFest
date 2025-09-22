# owner:valentin-alexa
# CRATE_DATE: 2024-06-20 10:40
# LAST MODIFY_DATE: --
# MODIFY BY: --
# models/review.py
from sqlalchemy import Column, Integer, ForeignKey, Date, Text, func
from sqlalchemy.orm import relationship

from database.engine import Base


class Review(Base):
    __tablename__ = "review"

    review_id = Column(Integer, primary_key=True, autoincrement=True)
    manager_id = Column(Integer, ForeignKey("employee.employee_id"), nullable=False)
    salesperson_id = Column(Integer, ForeignKey("employee.employee_id"), nullable=False)
    review_date = Column(Date, nullable=False, server_default=func.current_date())
    review_text = Column(Text, nullable=False)

    # relații opționale (dacă ai Employee model)
    manager = relationship("Employee", foreign_keys=[manager_id], lazy="joined")
    salesperson = relationship("Employee", foreign_keys=[salesperson_id], lazy="joined")
