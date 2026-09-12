import Link from "next/link";
import { transactions } from "@/modules/transactions/data";
import { reconcileTransaction } from "@/modules/reconciliation/rules";
import { Header, SeverityBadge } from "@/components/ui";

export default function Home() {
  const investigations = transactions.map((transaction) => ({
    transaction,
    findings: reconcileTransaction(transaction),
  }));
  const counts = investigations.reduce(
    (summary, { findings }) => {
      const status = findings.some((finding) => finding.severity === "critical")
        ? "broken"
        : findings.length > 0
          ? "warning"
          : "healthy";
      summary[status] += 1;
      return summary;
    },
    { healthy: 0, warning: 0, broken: 0 },
  );
  const priority = investigations
    .filter(({ findings }) => findings.length > 0)
    .sort((a, b) => b.findings.length - a.findings.length)
    .slice(0, 4);

  return (
    <>
      <Header />
      <main className="mx-auto max-w-7xl px-6 py-10">
        <p className="eyebrow">Investigation command center</p>
        <div className="mt-2 flex flex-wrap items-end justify-between gap-4">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">Commercial integrity, in one view.</h1>
            <p className="mt-2 text-slate-500">Trace every invoice from creation to cash, and resolve breaks with evidence.</p>
          </div>
          <Link className="button" href="/transactions">Investigate transactions <span aria-hidden>→</span></Link>
        </div>

        <section className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4" aria-label="Portfolio summary">
          <Metric label="Transactions tracked" value={transactions.length} detail="Mock investigation dataset" />
          <Metric label="Healthy" value={counts.healthy} detail="Complete commercial lineage" tone="healthy" />
          <Metric label="Needs attention" value={counts.warning} detail="Review before close" tone="warning" />
          <Metric label="Broken" value={counts.broken} detail="Resolution required" tone="critical" />
        </section>

        <section className="mt-10 grid gap-6 lg:grid-cols-[1.6fr_1fr]">
          <div className="panel">
            <div className="flex items-center justify-between">
              <div><p className="eyebrow">Priority queue</p><h2 className="mt-1 text-xl font-semibold">Recent investigations</h2></div>
              <Link href="/transactions" className="text-sm font-semibold text-teal-700 hover:text-teal-900">View all</Link>
            </div>
            <div className="mt-5 divide-y divide-slate-100">
              {priority.map(({ transaction, findings }) => (
                <Link key={transaction.id} href={`/transactions/${transaction.id}`} className="flex items-center justify-between gap-4 py-4 transition hover:bg-slate-50">
                  <div><p className="font-semibold">{transaction.invoiceNumber} <span className="font-normal text-slate-500">· {transaction.customer}</span></p><p className="mt-1 text-sm text-slate-500">{findings[0].title}</p></div>
                  <SeverityBadge severity={findings.some((f) => f.severity === "critical") ? "critical" : "warning"} />
                </Link>
              ))}
            </div>
          </div>
          <aside className="rounded-2xl bg-slate-900 p-6 text-slate-100">
            <p className="eyebrow text-teal-300">How it works</p>
            <h2 className="mt-2 text-xl font-semibold">Evidence before explanation.</h2>
            <ol className="mt-6 space-y-5 text-sm text-slate-300">
              <li><span className="mr-3 inline-flex h-6 w-6 items-center justify-center rounded-full bg-teal-400 font-semibold text-slate-950">1</span> Follow the document and money lifecycle.</li>
              <li><span className="mr-3 inline-flex h-6 w-6 items-center justify-center rounded-full bg-teal-400 font-semibold text-slate-950">2</span> Apply deterministic reconciliation rules.</li>
              <li><span className="mr-3 inline-flex h-6 w-6 items-center justify-center rounded-full bg-teal-400 font-semibold text-slate-950">3</span> Act on a grounded resolution plan.</li>
            </ol>
          </aside>
        </section>
      </main>
    </>
  );
}

function Metric({ label, value, detail, tone }: { label: string; value: number; detail: string; tone?: "healthy" | "warning" | "critical" }) {
  return <div className={`panel border-l-4 ${tone === "healthy" ? "border-l-emerald-500" : tone === "warning" ? "border-l-amber-400" : tone === "critical" ? "border-l-rose-500" : "border-l-slate-300"}`}><p className="text-sm font-medium text-slate-500">{label}</p><p className="mt-3 text-3xl font-semibold">{value}</p><p className="mt-1 text-sm text-slate-400">{detail}</p></div>;
}
