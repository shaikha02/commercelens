# CommerceLens

CommerceLens is a runnable transaction-investigation MVP. It traces deterministic mock commerce records through **Invoice → AR → GL → Revenue → Tax → Receipt**, flags reconciliation breaks, and presents evidence-led resolution guidance.

## Run locally

Requires Node.js 20.19+.

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). No credentials, database, API key, or external integrations are required.

## Commands

```bash
npm run lint    # ESLint
npm test        # reconciliation rule unit tests
npm run build   # production build
npm start       # serve a production build
```

## Demo data and behavior

Ten stable, in-memory transactions cover healthy, warning, and broken states. The rules detect missing GL after AR, invoice/revenue mismatches, missing tax events for taxable invoices, and receipt/balance mismatches. The investigation explanation is generated locally from the rule findings and event evidence; it does not call an LLM or make unsupported claims.

## Structure

- `src/modules/transactions` — types and deterministic seed records
- `src/modules/reconciliation` — modular, tested reconciliation rules
- `src/modules/evidence` — deterministic grounded explanation builder
- `src/components` — reusable UI
- `src/app` — Next.js App Router screens
