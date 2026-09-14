from functools import lru_cache

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.repositories.json_repository import JsonRepository
from app.repositories.transaction_repository import TransactionRepository
from app.services.event_service import EventService
from app.services.lineage_service import LineageService
from app.services.transaction_service import TransactionService


@lru_cache
def get_json_repository(data_dir: str) -> JsonRepository:
    return JsonRepository(data_dir)


def get_transaction_repository(settings: Settings = Depends(get_settings)) -> TransactionRepository:
    return TransactionRepository(JsonRepository(settings.data_dir))


def get_transaction_service(repository: TransactionRepository = Depends(get_transaction_repository)) -> TransactionService:
    return TransactionService(repository)


def get_lineage_service(repository: TransactionRepository = Depends(get_transaction_repository)) -> LineageService:
    return LineageService(repository)


def get_event_service(repository: TransactionRepository = Depends(get_transaction_repository)) -> EventService:
    return EventService(repository)
