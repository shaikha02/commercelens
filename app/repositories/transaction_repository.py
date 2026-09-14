from collections.abc import Mapping
from threading import Lock
from typing import TypeVar

from pydantic import BaseModel

from app.models.event import Event
from app.models.invoice import Invoice
from app.models.records import ARRecord, GLRecord, RevenueRecord, TaxReceipt, TaxReport, Transformation
from app.repositories.json_repository import JsonRepository

ModelT = TypeVar("ModelT", bound=BaseModel)


class TransactionRepository:
    def __init__(self, json_repository: JsonRepository):
        self.json_repository = json_repository
        self._invoice_indexes: dict[str, dict[str, Mapping[str, object]]] = {}
        self._transformation_index: dict[str, Mapping[str, object]] | None = None
        self._event_index: dict[str, list[Event]] | None = None
        self._index_lock = Lock()

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
        if self._transformation_index is None:
            with self._index_lock:
                if self._transformation_index is None:
                    self._transformation_index = {
                        str(item["version"]): item for item in self.json_repository.load_collection("transformations.json")
                    }
        item = self._transformation_index.get(version)
        if item is not None:
            return Transformation.model_validate(item)
        return None

    def list_events(self, invoice_id: str) -> list[Event]:
        if self._event_index is None:
            with self._index_lock:
                if self._event_index is None:
                    event_index: dict[str, list[Event]] = {}
                    for item in self.json_repository.load_collection("events.json"):
                        event = Event.model_validate(item)
                        event_index.setdefault(event.invoice_id, []).append(event)
                    for events in event_index.values():
                        events.sort(key=lambda event: event.timestamp)
                    self._event_index = event_index
        return list(self._event_index.get(invoice_id, []))

    def _find_one(self, filename: str, model: type[ModelT], invoice_id: str) -> ModelT | None:
        index = self._invoice_indexes.get(filename)
        if index is None:
            with self._index_lock:
                index = self._invoice_indexes.get(filename)
                if index is None:
                    index = {}
                    for item_index, item in enumerate(self.json_repository.load_collection(filename)):
                        if "invoice_id" not in item:
                            raise ValueError(f"Expected {filename}[{item_index}] to contain an invoice_id")
                        index[str(item["invoice_id"])] = item
                    self._invoice_indexes[filename] = index
        item = index.get(invoice_id)
        if item is not None:
            return model.model_validate(item)
        return None
