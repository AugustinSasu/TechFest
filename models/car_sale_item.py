# owner:valentin-alexa
# CRATE_DATE: 2024-06-20 10:40
# LAST MODIFY_DATE: --
# MODIFY BY: --
# models/car_sale_item.py
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, ForeignKey, Numeric, UniqueConstraint
from database.engine import Base
# descriere tabela car_sale_item
class CarSaleItem(Base):
    __tablename__ = "car_sale_item"
    __table_args__ = (UniqueConstraint("order_id", "vehicle_id", name="uq_car_sale_item_order_vehicle"), )

    item_id:   Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id:  Mapped[int] = mapped_column(ForeignKey("sale_order.order_id", ondelete="CASCADE"), nullable=False)
    vehicle_id:Mapped[int] = mapped_column(ForeignKey("vehicle.vehicle_id"), nullable=False)
    unit_price:Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
