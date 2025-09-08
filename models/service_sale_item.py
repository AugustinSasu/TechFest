# 📁 models/service_sale_item.py
# ✅ MODEL: service_sale_item.py
# -------------------------------
# Reprezintă tabela `service_sale_item` din Oracle DB.
# Folosit pentru a înregistra vânzarea de servicii (CASCO, extra opțiuni etc.) într-o comandă.
# Are legături către:
# - `sale_order` (prin order_id)
# - `service_item` (prin service_id)
#
# 🧠 Observație: Coloana `line_total` este VIRTUALĂ în Oracle (qty * unit_price),
# deci nu trebuie să o setăm la inserare, doar să o citim la citire (read-only).

from sqlalchemy import Column, Integer, Numeric, ForeignKey
from database.engine import Base

class ServiceSaleItem(Base):
    __tablename__ = "service_sale_item"

    item_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("sale_order.order_id", ondelete="CASCADE"), nullable=False)
    service_id = Column(Integer, ForeignKey("service_item.service_id"), nullable=False)
    qty = Column(Numeric(6, 2), nullable=False, default=1)
    unit_price = Column(Numeric(12, 2), nullable=False)
    # line_total este definit virtual în Oracle, deci îl tratăm doar la citire (nu îl includem în CREATE)

    # ⚠️ Dacă dorim să îl includem în response_model, îl calculăm manual în service / schema
