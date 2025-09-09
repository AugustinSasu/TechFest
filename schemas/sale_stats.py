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