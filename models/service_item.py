from sqlalchemy import Column, Integer, String, Numeric
from database.engine import Base

class ServiceItem(Base):
    __tablename__ = "service_item"

    service_id   = Column(Integer, primary_key=True, autoincrement=True)
    service_type = Column(String(24), nullable=False)  # see CHECK in DB
    name         = Column(String(120), nullable=False)
    description  = Column(String(4000))
    list_price   = Column(Numeric(12, 2))
