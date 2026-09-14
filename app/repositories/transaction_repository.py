from app.models.event import Event
from app.models.invoice import Invoice
from app.models.records import ARRecord, GLRecord, RevenueRecord, TaxReceipt, TaxReport, Transformation
from app.repositories.json_repository import JsonRepository


class TransactionRepository:
    def __init__(self, json_repository: JsonRepository):
        self.json_repository = json_repository

    def get_invoice(self, invoice_id: str) -> Invoice | None:
        return self._find_one("invoices.json", Invoice, invoice_id)

    def get_ar_record(self, invoice_id: str) -> ARRecord | None:
        return self._find_one("ar_records.json", ARRecord, invoice_id)

    def get_gl_record(self, invoice_id: str) -> GLRecord | None:
        return self._find_one("gl_records.json", GLRecord, invoice_id)

    def get_revenue_record(self, invoice_id: str) -> RevenueRecord | None:
        return self._find_one("revenue_records.json", RevenueRecord, invoice_id)

    def get_tax_report(self, invoice_id: str) -> TaxReport | None:
        return self._find_one("tax_reports.json", TaxReport, invoice_id)

    def get_tax_receipt(self, invoice_id: str) -> TaxReceipt | None:
        return self._find_one("tax_receipts.json", TaxReceipt, invoice_id)

    def get_transformation(self, version: str) -> Transformation | None:
        for item in self.json_repository.load_collection("transformations.json"):
            if item.get("version") == version:
                return Transformation.model_validate(item)
        return None

    def list_events(self, invoice_id: str) -> list[Event]:
        events = [
            Event.model_validate(item)
            for item in self.json_repository.load_collection("events.json")
            if item.get("invoice_id") == invoice_id
        ]
        return sorted(events, key=lambda event: event.timestamp)

    def _find_one(self, filename: str, model: type, invoice_id: str):
        for item in self.json_repository.load_collection(filename):
            if item.get("invoice_id") == invoice_id:
                return model.model_validate(item)
        return None
