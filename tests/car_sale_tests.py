import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app

#TODO write tests for car sale item repository
#         stmt = stmt.where(*conds)
#         order_func = asc if sort == "asc" else desc
#         if sort_by == "order_id":
#             stmt = stmt.order_by(order_func(CarSaleItem.order_id))
#         else:
#             stmt = stmt.order_by(order_func(CarSaleItem.item_id))
#         stmt = stmt.offset(skip).limit(limit)
#         return db.execute(stmt).scalars().all()
t