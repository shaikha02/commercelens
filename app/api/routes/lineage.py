from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_lineage_service
from app.models.lineage import LineageGraph
from app.services.lineage_service import LineageService

router = APIRouter(prefix="/invoices", tags=["lineage"])


@router.get("/{invoice_id}/lineage", response_model=LineageGraph)
def get_invoice_lineage(invoice_id: str, service: LineageService = Depends(get_lineage_service)) -> LineageGraph:
    lineage = service.get_lineage(invoice_id)
    if lineage is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invoice {invoice_id} not found")
    return lineage
