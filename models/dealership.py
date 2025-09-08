from sqlalchemy import Column, Integer, String
from database.engine import Base

class Dealership(Base):
    __tablename__ = "dealership"

    dealership_id = Column(Integer, primary_key=True, autoincrement=True)
    name          = Column(String(100), nullable=False)
    city          = Column(String(80))
    region        = Column(String(80))
