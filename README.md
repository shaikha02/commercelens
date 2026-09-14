# CommerceLens Phase-1 Backend

CommerceLens Phase 1 is a deterministic mock backend for tracing one commerce transaction across invoice, AR, GL, revenue, tax reporting, and tax receipt stages. It intentionally uses local JSON fixtures only. There is no actual AI integration, cloud service, database, message bus, or frontend in Phase 1.

## Architecture

The application follows a thin layered flow:

```text
FastAPI route -> Service -> Repository -> local JSON files
```

Routes use FastAPI dependency injection (`Depends`) and Pydantic v2 response models. JSON files live in `data/`, and data paths are resolved from the source tree so the app does not depend on the shell's current working directory.

## Prerequisites

- Python 3.11+
- `pip`

## Setup and installation

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Running

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Swagger UI is available at <http://127.0.0.1:8000/docs> after the server starts.

## API examples

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/v1/invoices/INV-1001
curl http://127.0.0.1:8000/api/v1/invoices/INV-8421/summary
curl http://127.0.0.1:8000/api/v1/invoices/INV-8421/lineage
curl http://127.0.0.1:8000/api/v1/invoices/INV-8421/events
```

Implemented endpoints:

- `GET /health`
- `GET /api/v1/invoices/{invoice_id}`
- `GET /api/v1/invoices/{invoice_id}/summary`
- `GET /api/v1/invoices/{invoice_id}/lineage`
- `GET /api/v1/invoices/{invoice_id}/events`

Unknown invoice IDs return HTTP 404 for all invoice-scoped endpoints.

## Local fixture behavior

The fixtures contain two invoices:

- `INV-1001`: healthy, fully complete lifecycle.
- `INV-8421`: deliberately broken. Its invoice total is `118000`, tax is `18000`, AR and GL are posted for `118000`, revenue is reported for `100000`, tax reporting is mismatched at taxable amount `98000` and tax amount `16000`, and the tax receipt remains `NOT_GENERATED`.

Events are filtered by invoice and sorted by parsed timezone-aware timestamps in repository logic. The stored fixture order is deliberately unsorted and interleaved to keep sorting behavior testable.

## Monetary serialization

Monetary fields are modeled and processed with Python `Decimal`. Fixture monetary values are stored as JSON strings for precision-safe ingestion. API responses serialize Decimal values as JSON strings to avoid binary floating-point rounding surprises.

## Testing

```bash
pytest
```

The tests cover health, valid and missing invoices, summaries, lineage topology and references, event filtering, chronological ordering from unsorted fixture input, and the exact broken invoice state.

## Phase-2 roadmap

These items are not implemented in Phase 1:

- Add real persistence and data ingestion connectors.
- Add authentication and authorization.
- Add richer diagnostics and explainability workflows.
- Add external system integrations after they are explicitly selected.
- Add an optional frontend or operational dashboard.
