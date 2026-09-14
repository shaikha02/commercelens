from datetime import date
from decimal import Decimal
from typing import Annotated, Any

from pydantic import BaseModel, PlainSerializer


MoneyDecimal = Annotated[Decimal, PlainSerializer(lambda value: str(value), return_type=str, when_used="json")]


class ARRecord(BaseModel):
    record_id: str
    invoice_id: str
    amount: MoneyDecimal
    currency: str
    status: str
    posted_date: date | None = None


class GLRecord(BaseModel):
    record_id: str
    invoice_id: str
    amount: MoneyDecimal
    currency: str
    status: str
    ledger_account: str
    posted_date: date | None = None


class RevenueRecord(BaseModel):
    record_id: str
    invoice_id: str
    amount: MoneyDecimal
    currency: str
    status: str
    recognition_date: date | None = None


class TaxReport(BaseModel):
    record_id: str
    invoice_id: str
    taxable_amount: MoneyDecimal
    tax_amount: MoneyDecimal
    currency: str
    transformation_version: str
    status: str
    submitted_date: date | None = None


class TaxReceipt(BaseModel):
    record_id: str
    invoice_id: str
    tax_report_id: str
    status: str
    receipt_reference: str | None = None
    generated_date: date | None = None


class Transformation(BaseModel):
    version: str
    name: str
    description: str
    source_record_type: str
    target_record_type: str
    rules: list[str]
    metadata: dict[str, Any] = {}
