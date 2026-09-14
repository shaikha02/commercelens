import json
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_transaction_repository
from app.main import app
from app.models.invoice import LifecycleStages
from app.repositories.json_repository import JsonRepository
from app.repositories.transaction_repository import TransactionRepository
from app.services.transaction_service import TransactionService

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


def test_broken_invoice_inv_8421_summary_is_partially_complete() -> None:
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


def test_lifecycle_completion_rules_match_summary_stage_fields() -> None:
    assert set(LifecycleStages.model_fields) == set(TransactionService.COMPLETE_STAGE_STATUSES)


def test_json_repository_rejects_non_array_fixture(tmp_path) -> None:
    (tmp_path / "bad.json").write_text('{"not": "a collection"}', encoding="utf-8")
    repository = JsonRepository(tmp_path)

    with pytest.raises(ValueError, match="Expected bad.json to contain a JSON array"):
        repository.load_collection("bad.json")


def test_json_repository_rejects_non_object_collection_item(tmp_path) -> None:
    (tmp_path / "bad.json").write_text('["not an object"]', encoding="utf-8")
    repository = JsonRepository(tmp_path)

    with pytest.raises(ValueError, match=r"Expected bad\.json\[0\] to contain a JSON object"):
        repository.load_collection("bad.json")


def test_existing_invoice_with_missing_downstream_records_uses_missing_fallbacks(tmp_path) -> None:
    (tmp_path / "invoices.json").write_text(
        json.dumps(
            [
                {
                    "invoice_id": "INV-MISSING",
                    "order_id": "ORD-MISSING",
                    "customer_id": "CUST-MISSING",
                    "currency": "USD",
                    "invoice_date": "2026-01-12",
                    "subtotal": "10.00",
                    "tax": "1.00",
                    "total": "11.00",
                    "status": "GENERATED",
                }
            ]
        ),
        encoding="utf-8",
    )
    for filename in [
        "ar_records.json",
        "gl_records.json",
        "revenue_records.json",
        "tax_reports.json",
        "tax_receipts.json",
        "transformations.json",
        "events.json",
    ]:
        (tmp_path / filename).write_text("[]\n", encoding="utf-8")

    repository = TransactionRepository(JsonRepository(tmp_path))
    app.dependency_overrides[get_transaction_repository] = lambda: repository
    try:
        summary_response = client.get("/api/v1/invoices/INV-MISSING/summary")
        lineage_response = client.get("/api/v1/invoices/INV-MISSING/lineage")
    finally:
        app.dependency_overrides.clear()

    assert summary_response.status_code == 200
    assert summary_response.json()["stages"] == {
        "invoice": "GENERATED",
        "ar": "MISSING",
        "gl": "MISSING",
        "revenue": "MISSING",
        "tax_reporting": "MISSING",
        "tax_receipt": "MISSING",
    }
    assert lineage_response.status_code == 200
    node_ids = {node["id"] for node in lineage_response.json()["nodes"]}
    assert {
        "ar:missing:INV-MISSING",
        "gl:missing:INV-MISSING",
        "revenue:missing:INV-MISSING",
        "tax_report:missing:INV-MISSING",
        "tax_receipt:missing:INV-MISSING",
    }.issubset(node_ids)


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
