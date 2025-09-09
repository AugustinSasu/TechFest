# models/sale_order.py
# MODEL: sale_order.py

# -------------------------
# Reprezintă header-ul unei comenzi de vânzare auto.
# Fiecare `sale_order` poate avea:
# - 0 sau 1 `car_sale_item`
# - 0 sau mai multe `service_sale_item`
# Este legat de: `dealership`, `customer`, `employee (sales & manager)`

# Autor: Alexa Cristian-Valentin
# Data: 09-09-2024
# -------------------------

from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey
from database.engine import Base

class SaleOrder(Base):
    __tablename__ = "sale_order"

    order_id = Column(Integer, primary_key=True, autoincrement=True)

    # 🔗 FK către alte entități
    dealership_id = Column(Integer, ForeignKey("dealership.dealership_id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customer.customer_id"), nullable=False)
    salesperson_id = Column(Integer, ForeignKey("employee.employee_id"), nullable=False)
    manager_id = Column(Integer, ForeignKey("employee.employee_id"))  # poate fi NULL

    # 📅 Metadata comandă
    order_date = Column(Date)
    status = Column(String(20))  # 'OPEN', 'APPROVED', 'INVOICED', 'CANCELLED'
    total_amount = Column(Numeric(14, 2))  # Poate fi calculat din itemi (dar e direct setat aici)
    created_by = Column(String(30))  # DB username (AUDIT)

    # 🔐 Conexiuni cu car_sale_item și service_sale_item se definesc în modelele respective