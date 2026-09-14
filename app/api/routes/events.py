from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_event_service
from app.models.event import Event
from app.services.event_service import EventService

router = APIRouter(prefix="/invoices", tags=["events"])


@router.get("/{invoice_id}/events", response_model=list[Event])
def get_invoice_events(invoice_id: str, service: EventService = Depends(get_event_service)) -> list[Event]:
    events = service.get_events(invoice_id)
    if events is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invoice {invoice_id} not found")
    return events
