from datetime import date

from pydantic import BaseModel

from app.models.common import MoneyDecimal


class Invoice(BaseModel):
    invoice_id: str
    order_id: str
    customer_id: str
    currency: str
    invoice_date: date
    subtotal: MoneyDecimal
    tax: MoneyDecimal
    total: MoneyDecimal
    status: str


class LifecycleStages(BaseModel):
    invoice: str
    ar: str
    gl: str
    revenue: str
    tax_reporting: str
    tax_receipt: str


class InvoiceSummary(BaseModel):
    invoice_id: str
    order_id: str
    currency: str
    lifecycle_status: str
    invoice_total: MoneyDecimal
    invoice_tax: MoneyDecimal
    stages: LifecycleStages
