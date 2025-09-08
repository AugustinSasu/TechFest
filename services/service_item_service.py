# --------------------------------------------------------------------
# Acest fișier definește logica de business pentru entitatea "service_item".
# Aceasta reprezintă servicii suplimentare asociate unei vânzări auto (ex: CASCO, închiriere, garanții etc).
# Layer-ul service apelează `ServiceItemRepository` pentru a accesa datele din baza de date.
#
# Autor: Cristian-Valentin Alexa
# Data: 14 Aprilie 2024
# Ora: 15:00
# --------------------------------------------------------------------


from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from repositories.service_item_repository import ServiceItemRepository as Repo
from schemas.service_item import ServiceItemCreate, ServiceItemUpdate
from models.service_item import ServiceItem

class ServiceItemService:
    @staticmethod
    def create(db: Session, data: ServiceItemCreate) -> ServiceItem:
        """
        Creează un nou obiect `ServiceItem` în DB pe baza datelor primite din payload (schema).
        """
        return Repo.create(db, data)

    @staticmethod
    def get(db: Session, service_id: int) -> Optional[ServiceItem]:
        """
        Returnează un service_item după ID, sau None dacă nu există.
        """
        return Repo.get(db, service_id)

    @staticmethod
    def list(
        db: Session,
        q: Optional[str],                    # caută în numele serviciului
        service_type: Optional[str],         # filtrează după tip: CASCO, EXTRA_OPTION etc
        sort: str,                           # "asc" sau "desc"
        limit: int,
        offset: int,
    ) -> List[ServiceItem]:
        """
        Returnează o listă de servicii filtrate și ordonate dinamic.
        Exemplu: /service-items?q=casco&service_type=CASCO&sort=asc
        """
        return Repo.list(
            db,
            q=q,
            service_type=service_type,
            sort=sort,
            limit=limit,
            offset=offset
        )

    @staticmethod
    def update(db: Session, service_id: int, data: ServiceItemUpdate) -> Optional[ServiceItem]:
        """
        Actualizează un obiect existent cu noile valori. Returnează None dacă nu a fost găsit.
        """
        return Repo.update(db, service_id, data)

    @staticmethod
    def delete(db: Session, service_id: int) -> bool:
        """
        Șterge obiectul `ServiceItem` din baza de date.
        Returnează True dacă a fost șters, False dacă nu există.
        """
        return Repo.delete(db, service_id)

    @staticmethod
    def export_json(db: Session) -> List[Dict[str, Any]]:
        """
        Exportă serviciile ca listă JSON serializabilă (pentru API / integrare).
        """
        rows = Repo.list(db, limit=10_000, offset=0, sort="asc")
        return [
            {
                "service_id": r.service_id,
                "service_type": r.service_type,
                "name": r.name,
                "description": r.description,
                "list_price": float(r.list_price or 0)
            }
            for r in rows
        ]

    @staticmethod
    def export_txt(db: Session) -> str:
        """
        Exportă serviciile sub formă de text tabelar (.txt)
        """
        rows = Repo.list(db, limit=10_000, offset=0, sort="asc")
        lines = ["service_id | service_type | name | description | list_price"]
        for r in rows:
            lines.append(
                f"{r.service_id} | {r.service_type} | {r.name} | {r.description or ''} | {float(r.list_price or 0)}"
            )
        return "\n".join(lines)
