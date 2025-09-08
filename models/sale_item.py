from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from database.engine import Base

class SaleItem(Base):
    __tablename__ = "sale_item"

    item_id    = Column(Integer, primary_key=True, autoincrement=True)
    order_id   = Column(Integer, ForeignKey("sale_order.order_id", ondelete="CASCADE"), nullable=False)
    item_type  = Column(String(10), nullable=False)  # 'CAR' | 'SERVICE'
    vehicle_id = Column(Integer, ForeignKey("vehicle.vehicle_id"))
    service_id = Column(Integer, ForeignKey("service_item.service_id"))
    qty        = Column(Numeric(6, 2), nullable=False, default=1)
    unit_price = Column(Numeric(12, 2), nullable=False)

    # În Oracle, `line_total` e VIRTUAL (qty * unit_price) — nu îl re-definim aici;
    # îl calculăm în layerul de răspuns când avem nevoie.
