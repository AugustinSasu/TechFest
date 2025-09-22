# owner:POP MIRCEA STEFAN
# CRATE_DATE: 2024-06-20 10:40
# LAST MODIFY_DATE: 22/09/2025
# MODIFY BY: POP MIRCEA STEFAN

from sqlalchemy import Column, Integer, String, Numeric
from database.engine import Base

class ServiceItem(Base):
    __tablename__ = "service_item"

    service_id   = Column(Integer, primary_key=True, autoincrement=True)
    service_type = Column(String(24), nullable=False)  # see CHECK in DB
    name         = Column(String(120), nullable=False)
    description  = Column(String(4000))
    list_price   = Column(Numeric(12, 2))
