from app.models.invoice import Invoice, InvoiceSummary, LifecycleStages
from app.repositories.transaction_repository import TransactionRepository


class TransactionService:
    COMPLETE_STAGE_STATUSES = {
        "invoice": "GENERATED",
        "ar": "POSTED",
        "gl": "POSTED",
        "revenue": "REPORTED",
        "tax_reporting": "REPORTED",
        "tax_receipt": "GENERATED",
    }

    def __init__(self, repository: TransactionRepository):
        self.repository = repository

    def get_invoice(self, invoice_id: str) -> Invoice | None:
        """Return an invoice or None when the invoice ID is unknown."""
        return self.repository.get_invoice(invoice_id)

    def get_summary(self, invoice_id: str) -> InvoiceSummary | None:
        """Return a derived summary or None when the invoice ID is unknown."""
        invoice = self.repository.get_invoice(invoice_id)
        if invoice is None:
            return None

        ar_record = self.repository.get_ar_record(invoice_id)
        gl_record = self.repository.get_gl_record(invoice_id)
        revenue_record = self.repository.get_revenue_record(invoice_id)
        tax_report = self.repository.get_tax_report(invoice_id)
        tax_receipt = self.repository.get_tax_receipt(invoice_id)

        stages = LifecycleStages(
            invoice=invoice.status,
            ar=ar_record.status if ar_record else "MISSING",
            gl=gl_record.status if gl_record else "MISSING",
            revenue=revenue_record.status if revenue_record else "MISSING",
            tax_reporting=tax_report.status if tax_report else "MISSING",
            tax_receipt=tax_receipt.status if tax_receipt else "MISSING",
        )
        lifecycle_status = "COMPLETE" if stages.model_dump() == self.COMPLETE_STAGE_STATUSES else "PARTIALLY_COMPLETE"
        return InvoiceSummary(
            invoice_id=invoice.invoice_id,
            order_id=invoice.order_id,
            currency=invoice.currency,
            lifecycle_status=lifecycle_status,
            invoice_total=invoice.total,
            invoice_tax=invoice.tax,
            stages=stages,
        )
