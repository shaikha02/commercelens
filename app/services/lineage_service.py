from app.models.lineage import LineageEdge, LineageGraph, LineageNode
from app.repositories.transaction_repository import TransactionRepository


class LineageService:
    def __init__(self, repository: TransactionRepository):
        self.repository = repository

    def get_lineage(self, invoice_id: str) -> LineageGraph | None:
        """Return a derived lineage graph or None when the invoice ID is unknown."""
        invoice = self.repository.get_invoice(invoice_id)
        if invoice is None:
            return None

        ar_record = self.repository.get_ar_record(invoice_id)
        gl_record = self.repository.get_gl_record(invoice_id)
        revenue_record = self.repository.get_revenue_record(invoice_id)
        tax_report = self.repository.get_tax_report(invoice_id)
        tax_receipt = self.repository.get_tax_receipt(invoice_id)
        transformation = self.repository.get_transformation(tax_report.transformation_version) if tax_report else None

        order_node_id = f"order:{invoice.order_id}"
        invoice_node_id = f"invoice:{invoice.invoice_id}"
        ar_node_id = f"ar:{ar_record.record_id}" if ar_record else f"ar:missing:{invoice.invoice_id}"
        gl_node_id = f"gl:{gl_record.record_id}" if gl_record else f"gl:missing:{invoice.invoice_id}"
        revenue_node_id = f"revenue:{revenue_record.record_id}" if revenue_record else f"revenue:missing:{invoice.invoice_id}"
        tax_report_node_id = f"tax_report:{tax_report.record_id}" if tax_report else f"tax_report:missing:{invoice.invoice_id}"
        tax_receipt_node_id = f"tax_receipt:{tax_receipt.record_id}" if tax_receipt else f"tax_receipt:missing:{invoice.invoice_id}"

        nodes = [
            LineageNode(
                id=order_node_id,
                type="Order",
                label=invoice.order_id,
                status="CREATED",
                metadata={"customer_id": invoice.customer_id},
            ),
            LineageNode(
                id=invoice_node_id,
                type="Invoice",
                label=invoice.invoice_id,
                status=invoice.status,
                metadata={"total": str(invoice.total), "tax": str(invoice.tax), "currency": invoice.currency},
            ),
            LineageNode(
                id=ar_node_id,
                type="AR",
                label=ar_record.record_id if ar_record else "Missing AR record",
                status=ar_record.status if ar_record else "MISSING",
                metadata={"amount": str(ar_record.amount), "currency": ar_record.currency} if ar_record else {},
            ),
            LineageNode(
                id=gl_node_id,
                type="GL",
                label=gl_record.record_id if gl_record else "Missing GL record",
                status=gl_record.status if gl_record else "MISSING",
                metadata={"amount": str(gl_record.amount), "ledger_account": gl_record.ledger_account} if gl_record else {},
            ),
            LineageNode(
                id=revenue_node_id,
                type="Revenue",
                label=revenue_record.record_id if revenue_record else "Missing revenue record",
                status=revenue_record.status if revenue_record else "MISSING",
                metadata={"amount": str(revenue_record.amount), "currency": revenue_record.currency} if revenue_record else {},
            ),
            LineageNode(
                id=tax_report_node_id,
                type="Tax Report",
                label=tax_report.record_id if tax_report else "Missing tax report",
                status=tax_report.status if tax_report else "MISSING",
                metadata={
                    "taxable_amount": str(tax_report.taxable_amount),
                    "tax_amount": str(tax_report.tax_amount),
                    "currency": tax_report.currency,
                    "transformation_version": tax_report.transformation_version,
                    "transformation": transformation.model_dump() if transformation else None,
                }
                if tax_report
                else {},
            ),
            LineageNode(
                id=tax_receipt_node_id,
                type="Tax Receipt",
                label=tax_receipt.record_id if tax_receipt else "Missing tax receipt",
                status=tax_receipt.status if tax_receipt else "MISSING",
                metadata={"tax_report_id": tax_receipt.tax_report_id, "receipt_reference": tax_receipt.receipt_reference} if tax_receipt else {},
            ),
        ]
        edges = [
            LineageEdge(source=order_node_id, target=invoice_node_id, type="GENERATES"),
            LineageEdge(source=invoice_node_id, target=ar_node_id, type="CREATES"),
            LineageEdge(source=ar_node_id, target=gl_node_id, type="POSTS_TO"),
            LineageEdge(source=invoice_node_id, target=revenue_node_id, type="CONTRIBUTES_TO"),
            LineageEdge(source=revenue_node_id, target=tax_report_node_id, type="TRANSFORMED_BY"),
            LineageEdge(source=tax_report_node_id, target=tax_receipt_node_id, type="GENERATES"),
        ]
        return LineageGraph(invoice_id=invoice_id, nodes=nodes, edges=edges)
