# owner:POP MIRCEA STEFAN
# CRATE_DATE: 2024-06-20 10:40
# LAST MODIFY_DATE: --
# MODIFY BY: --
# schemas/sales_stats.py
from datetime import datetime
from pydantic import BaseModel
class SalesOrderStatOut(BaseModel):
    sale_id: int
    agent: str
    nume_locatie: str
    produs: str
    pret: float
    data_vanzare: datetime
    regiune: str