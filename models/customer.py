# owner:POP MIRCEA STEFAN
# CRATE_DATE: 2024-06-20 10:40
# LAST MODIFY_DATE: --
# MODIFY BY: --
# descriere tabela dealership
# tabela obiect identica cu tabela din baza de date oracle


from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String

class Base(DeclarativeBase):
    pass

class Customer(Base):
    __tablename__ = "customer"

    customer_id: Mapped[int] = mapped_column(Integer, primary_key=True)  # IDENTITY în Oracle
    full_name:   Mapped[str] = mapped_column(String(120), nullable=False)
    phone:       Mapped[str | None] = mapped_column(String(40))
    email:       Mapped[str | None] = mapped_column(String(120))
