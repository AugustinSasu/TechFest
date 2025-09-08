# ---------------------------------------------------------
# Acest fișier definește logica de business pentru entitatea "vehicle" (autoturisme).
# Acțiunile sunt organizate sub formă de metode statice în clasa `VehicleService`, care este apelată
# de către layerul de routing (FastAPI) și comunică direct cu `VehicleRepository` pentru acces la DB.
# 
# Autor: Cristian-Valentin Alexa
# Data: 14 Aprilie 2024
# Ora: 13:59
# ---------------------------------------------------------

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from repositories.vehicle_repository import VehicleRepository as Repo
from schemas.vehicle import VehicleCreate, VehicleUpdate
from models.vehicle import Vehicle

class VehicleService:
    @staticmethod
    def create(db: Session, data: VehicleCreate) -> Vehicle:
        """
        Creează un nou vehicul în baza de date.

        Parametri:
        - db: sesiunea activă SQLAlchemy
        - data: obiect Pydantic `VehicleCreate` care conține câmpurile necesare

        Returnează:
        - instanță a modelului `Vehicle`, persistată în DB
        """
        return Repo.create(db, data)

    @staticmethod
    def get(db: Session, vehicle_id: int) -> Optional[Vehicle]:
        """
        Obține un vehicul după ID.

        Parametri:
        - vehicle_id: identificatorul primar din tabelul `vehicle`

        Returnează:
        - obiect `Vehicle` sau `None` dacă nu există
        """
        return Repo.get(db, vehicle_id)

    @staticmethod
    def list(
        db: Session,
        q: Optional[str],                 # cautare în VIN / model
        model_year: Optional[int],       # filtrare exactă după an model
        min_price: Optional[float],      # preț minim
        max_price: Optional[float],      # preț maxim
        sort: str,                       # ordonare alfabetică după model
        limit: int,
        offset: int,
    ) -> List[Vehicle]:
        """
        Returnează o listă de vehicule, filtrată și ordonată după parametrii oferiți.

        Exemplu: /vehicles?q=golf&model_year=2023&sort=desc
        """
        return Repo.list(
            db,
            q=q,
            model_year=model_year,
            min_price=min_price,
            max_price=max_price,
            sort=sort,
            limit=limit,
            offset=offset
        )

    @staticmethod
    def update(db: Session, vehicle_id: int, data: VehicleUpdate) -> Optional[Vehicle]:
        """
        Actualizează un vehicul existent, doar cu câmpurile furnizate.
        Se folosește `.model_dump(exclude_unset=True)` pentru update parțial.

        Returnează:
        - noul obiect `Vehicle` actualizat sau `None` dacă nu a fost găsit
        """
        return Repo.update(db, vehicle_id, data)

    @staticmethod
    def delete(db: Session, vehicle_id: int) -> bool:
        """
        Șterge un vehicul din baza de date.

        Returnează:
        - True dacă vehiculul a fost găsit și șters, False dacă nu a fost găsit
        """
        return Repo.delete(db, vehicle_id)

    @staticmethod
    def export_json(db: Session) -> List[Dict[str, Any]]:
        """
        Exportă vehiculele sub formă de listă de dicționare (JSON serializabil).
        Folosit pentru endpoint-ul: GET /vehicles/export/json

        Returnează:
        - listă de obiecte {vehicle_id, vin, model, trim_level, model_year, base_price}
        """
        rows = Repo.list(db, limit=10_000, offset=0, sort="asc")
        return [
            {
                "vehicle_id": r.vehicle_id,
                "vin": r.vin,
                "model": r.model,
                "trim_level": r.trim_level,
                "model_year": r.model_year,
                "base_price": float(r.base_price or 0)
            }
            for r in rows
        ]

    @staticmethod
    def export_txt(db: Session) -> str:
        """
        Exportă vehiculele ca text, ideal pentru salvare locală (.txt).
        Se folosește separatorul | între coloane și fiecare vehicul e pe linie nouă.

        Returnează:
        - string formatat gata de scriere într-un fișier text
        """
        rows = Repo.list(db, limit=10_000, offset=0, sort="asc")
        lines = ["vehicle_id | vin | model | trim_level | model_year | base_price"]
        for r in rows:
            lines.append(
                f"{r.vehicle_id} | {r.vin or ''} | {r.model} | {r.trim_level or ''} | "
                f"{r.model_year or ''} | {float(r.base_price or 0)}"
            )
        return "\n".join(lines)