from app.models.event import Event
from app.repositories.transaction_repository import TransactionRepository


class EventService:
    def __init__(self, repository: TransactionRepository):
        self.repository = repository

    def get_events(self, invoice_id: str) -> list[Event] | None:
        """Return sorted invoice events or None when the invoice ID is unknown."""
        if self.repository.get_invoice(invoice_id) is None:
            return None
        return self.repository.list_events(invoice_id)
