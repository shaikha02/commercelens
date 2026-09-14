from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_transaction_service
from app.models.invoice import Invoice, InvoiceSummary
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/invoices", tags=["invoices"])


def _not_found(invoice_id: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invoice {invoice_id} not found")


@router.get("/{invoice_id}", response_model=Invoice)
def get_invoice(invoice_id: str, service: TransactionService = Depends(get_transaction_service)) -> Invoice:
    invoice = service.get_invoice(invoice_id)
    if invoice is None:
        raise _not_found(invoice_id)
    return invoice


@router.get("/{invoice_id}/summary", response_model=InvoiceSummary)
def get_invoice_summary(invoice_id: str, service: TransactionService = Depends(get_transaction_service)) -> InvoiceSummary:
    summary = service.get_summary(invoice_id)
    if summary is None:
        raise _not_found(invoice_id)
    return summary
