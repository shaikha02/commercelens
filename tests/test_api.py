from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


EXPECTED_EVENT_TYPES = [
    "InvoiceCreated",
    "InvoicePDFGenerated",
    "TaxInvoiceGenerated",
    "ARPosted",
    "GLPosted",
    "RevenueReported",
    "TaxReported",
    "TaxReceiptGenerated",
]

EXPECTED_BROKEN_SUCCEEDED_EVENT_TYPES = [
    "InvoiceCreated",
    "InvoicePDFGenerated",
    "TaxInvoiceGenerated",
    "ARPosted",
    "GLPosted",
    "RevenueReported",
]


INVOICE_ENDPOINTS = [
    "/api/v1/invoices/UNKNOWN",
    "/api/v1/invoices/UNKNOWN/summary",
    "/api/v1/invoices/UNKNOWN/lineage",
    "/api/v1/invoices/UNKNOWN/events",
]


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_valid_invoice_uses_decimal_string_amounts() -> None:
    response = client.get("/api/v1/invoices/INV-8421")
    assert response.status_code == 200
    body = response.json()
    assert body["invoice_id"] == "INV-8421"
    assert body["order_id"] == "ORD-8421"
    assert body["subtotal"] == "100000"
    assert body["tax"] == "18000"
    assert body["total"] == "118000"


def test_missing_invoice_endpoints_return_404() -> None:
    for endpoint in INVOICE_ENDPOINTS:
        response = client.get(endpoint)
        assert response.status_code == 404, endpoint


def test_broken_invoice_summary_state() -> None:
    response = client.get("/api/v1/invoices/INV-8421/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["lifecycle_status"] == "PARTIALLY_COMPLETE"
    assert body["invoice_total"] == "118000"
    assert body["invoice_tax"] == "18000"
    assert body["stages"] == {
        "invoice": "GENERATED",
        "ar": "POSTED",
        "gl": "POSTED",
        "revenue": "REPORTED",
        "tax_reporting": "MISMATCH",
        "tax_receipt": "NOT_GENERATED",
    }


def test_healthy_invoice_summary_is_complete() -> None:
    response = client.get("/api/v1/invoices/INV-1001/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["lifecycle_status"] == "COMPLETE"
    assert body["stages"] == {
        "invoice": "GENERATED",
        "ar": "POSTED",
        "gl": "POSTED",
        "revenue": "REPORTED",
        "tax_reporting": "REPORTED",
        "tax_receipt": "GENERATED",
    }


def test_lineage_topology_and_references() -> None:
    response = client.get("/api/v1/invoices/INV-8421/lineage")
    assert response.status_code == 200
    body = response.json()
    nodes = {node["id"]: node for node in body["nodes"]}
    assert len(nodes) == len(body["nodes"])
    node_ids = set(nodes)
    assert {(edge["source"], edge["type"], edge["target"]) for edge in body["edges"]} == {
        ("order:ORD-8421", "GENERATES", "invoice:INV-8421"),
        ("invoice:INV-8421", "CREATES", "ar:AR-8421"),
        ("ar:AR-8421", "POSTS_TO", "gl:GL-8421"),
        ("invoice:INV-8421", "CONTRIBUTES_TO", "revenue:REV-8421"),
        ("revenue:REV-8421", "TRANSFORMED_BY", "tax_report:TAXREP-8421"),
        ("tax_report:TAXREP-8421", "GENERATES", "tax_receipt:TAXRCPT-8421"),
    }
    for edge in body["edges"]:
        assert edge["source"] in node_ids
        assert edge["target"] in node_ids
    assert nodes["tax_report:TAXREP-8421"]["status"] == "MISMATCH"
    assert nodes["tax_report:TAXREP-8421"]["metadata"]["taxable_amount"] == "98000"
    assert nodes["tax_report:TAXREP-8421"]["metadata"]["tax_amount"] == "16000"
    assert nodes["tax_report:TAXREP-8421"]["metadata"]["transformation_version"] == "V3.2"
    assert nodes["tax_report:TAXREP-8421"]["metadata"]["transformation"]["version"] == "V3.2"
    assert nodes["tax_receipt:TAXRCPT-8421"]["status"] == "NOT_GENERATED"


def test_events_are_filtered_and_sorted_chronologically() -> None:
    response = client.get("/api/v1/invoices/INV-8421/events")
    assert response.status_code == 200
    events = response.json()
    assert [event["event_type"] for event in events] == EXPECTED_EVENT_TYPES
    assert {event["invoice_id"] for event in events} == {"INV-8421"}
    timestamps = [datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00")) for event in events]
    assert timestamps == sorted(timestamps)


def test_broken_invoice_event_failures_are_exact() -> None:
    response = client.get("/api/v1/invoices/INV-8421/events")
    assert response.status_code == 200
    events = {event["event_type"]: event for event in response.json()}
    for event_type in EXPECTED_BROKEN_SUCCEEDED_EVENT_TYPES:
        assert events[event_type]["status"] == "SUCCEEDED"
        assert events[event_type]["error_message"] is None
    assert events["TaxReported"]["status"] == "FAILED"
    assert events["TaxReported"]["error_message"] == "Country mapping mismatch"
    assert events["TaxReceiptGenerated"]["status"] == "FAILED"
    assert events["TaxReceiptGenerated"]["error_message"] == "Submission rejected because tax reporting record was invalid"


def test_healthy_invoice_events_all_succeed_and_are_isolated() -> None:
    response = client.get("/api/v1/invoices/INV-1001/events")
    assert response.status_code == 200
    events = response.json()
    assert [event["event_type"] for event in events] == EXPECTED_EVENT_TYPES
    assert {event["invoice_id"] for event in events} == {"INV-1001"}
    assert {event["status"] for event in events} == {"SUCCEEDED"}
