from typing import List, Optional
from sqlalchemy.orm import Session
from repositories.service_item_repository import ServiceItemRepository as Repo
from schemas.service_item import ServiceItemCreate, ServiceItemUpdate
from models.service_item import ServiceItem

class ServiceItemService:
    @staticmethod
    def create(db: Session, data: ServiceItemCreate) -> ServiceItem:
        return Repo.create(db, data)

    @staticmethod
    def get(db: Session, service_id: int) -> Optional[ServiceItem]:
        return Repo.get(db, service_id)

    @staticmethod
    def list(
        db: Session,
        q: Optional[str],
        service_type: Optional[str],
        sort: str,
        limit: int,
        offset: int,
    ) -> List[ServiceItem]:
        return Repo.list(db, q=q, service_type=service_type, sort=sort, limit=limit, offset=offset)

    @staticmethod
    def update(db: Session, service_id: int, data: ServiceItemUpdate) -> Optional[ServiceItem]:
        return Repo.update(db, service_id, data)

    @staticmethod
    def delete(db: Session, service_id: int) -> bool:
        return Repo.delete(db, service_id)
