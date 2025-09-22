# owner:POP MIRCEA STEFAN
# CRATE_DATE: 2024-06-20 10:40
# LAST MODIFY_DATE: --
# MODIFY BY: --
from sqlalchemy import Column, Integer, String, Numeric
from database.engine import Base

class Vehicle(Base):
    __tablename__ = "vehicle"

    vehicle_id = Column(Integer, primary_key=True, autoincrement=True)
    vin        = Column(String(32), unique=True)
    model      = Column(String(60), nullable=False)
    trim_level = Column(String(60))
    model_year = Column(Integer)
    base_price = Column(Numeric(12, 2))
