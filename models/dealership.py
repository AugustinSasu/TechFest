# owner:POP MIRCEA STEFAN
# CRATE_DATE: 2024-06-20 10:40
# LAST MODIFY_DATE: --
# MODIFY BY: --
# descriere tabela dealership
# tabela obiect identica cu tabela din baza de date oracle

from sqlalchemy import Column, Integer, String
from database.engine import Base

class Dealership(Base):
    __tablename__ = "dealership"

    dealership_id = Column(Integer, primary_key=True, autoincrement=True)
    name          = Column(String(100), nullable=False)
    city          = Column(String(80))
    region        = Column(String(80))
