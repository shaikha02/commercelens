import Link from "next/link";
import { notFound } from "next/navigation";
import { Header, SeverityBadge } from "@/components/ui";
import { getTransaction } from "@/modules/transactions/data";
import { systems } from "@/modules/transactions/types";
import { reconcileTransaction } from "@/modules/reconciliation/rules";
import { createExplanation } from "@/modules/evidence/explanation";

export default async function InvestigationPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const transaction = getTransaction(id);
  if (!transaction) notFound();
  const findings = reconcileTransaction(transaction);
  const explanation = createExplanation(transaction, findings);
  const severity = findings.some((finding) => finding.severity === "critical") ? "critical" : findings.length ? "warning" : "healthy";
  return <><Header /><main className="mx-auto max-w-7xl px-6 py-8">
    <Link href="/transactions" className="text-sm font-semibold text-teal-700">← All transactions</Link>
    <div className="mt-5 flex flex-wrap items-start justify-between gap-4"><div><p className="eyebrow">Investigation</p><h1 className="mt-1 text-3xl font-semibold tracking-tight">{transaction.invoiceNumber}</h1><p className="mt-1 text-slate-500">{transaction.customer} · {transaction.currency} {transaction.invoiceTotal.toLocaleString()}</p></div><SeverityBadge severity={severity} /></div>
    <section className="mt-8"><div className="flex items-center justify-between"><h2 className="text-xl font-semibold">Commercial lineage</h2><span className="text-sm text-slate-500">{transaction.events.length} of 6 systems evidenced</span></div>
      <ol className="mt-5 grid gap-3 md:grid-cols-6">{systems.map((system, index) => { const event = transaction.events.find((item) => item.system === system); return <li key={system} className={`relative rounded-xl border p-4 ${event ? "border-teal-200 bg-white" : "border-dashed border-rose-300 bg-rose-50"}`}><span className="text-xs font-bold text-slate-400">0{index + 1}</span><p className="mt-2 font-semibold">{system}</p>{event ? <><p className="mt-2 text-sm font-medium text-slate-700">{event.currency} {event.amount.toLocaleString()}</p><p className="mt-1 break-all text-xs text-slate-500">{event.reference}</p></> : <p className="mt-2 text-sm font-medium text-rose-700">No event found</p>}</li>})}</ol>
    </section>
    <section className="mt-10 grid gap-6 lg:grid-cols-[1.25fr_1fr]">
      <div className="panel"><p className="eyebrow">Detected findings</p><h2 className="mt-1 text-xl font-semibold">{findings.length ? `${findings.length} exception${findings.length > 1 ? "s" : ""} detected` : "No exceptions detected"}</h2><div className="mt-5 space-y-4">{findings.length ? findings.map((finding) => <article key={finding.id} className="rounded-xl border border-slate-200 p-4"><div className="flex justify-between gap-3"><h3 className="font-semibold">{finding.title}</h3><SeverityBadge severity={finding.severity} /></div><p className="mt-3 text-sm text-slate-600"><strong>Evidence:</strong> {finding.evidence}</p><p className="mt-2 text-sm text-slate-600"><strong>Resolution:</strong> {finding.recommendation}</p></article>) : <p className="rounded-xl bg-emerald-50 p-4 text-sm text-emerald-800">Every required lifecycle event is present and its amount matches the invoice.</p>}</div></div>
      <aside className="rounded-2xl bg-teal-950 p-6 text-white"><p className="eyebrow text-teal-300">Grounded explanation</p><h2 className="mt-1 text-xl font-semibold">Deterministic investigation brief</h2><ExplanationSection label="Evidence" content={explanation.evidence} /><ExplanationSection label="Likely root cause" content={explanation.rootCause} /><ExplanationSection label="Recommended next action" content={explanation.action} /></aside>
    </section>
    <section className="panel mt-6"><p className="eyebrow">Event evidence</p><h2 className="mt-1 text-xl font-semibold">Source records</h2><div className="mt-4 overflow-x-auto"><table><thead><tr><th>System</th><th>Source reference</th><th>Amount</th><th>Timestamp</th><th>Status</th></tr></thead><tbody>{transaction.events.map((event) => <tr key={event.id}><td className="font-semibold">{event.system}</td><td className="font-mono text-xs">{event.reference}</td><td>{event.currency} {event.amount.toLocaleString()}</td><td>{new Date(event.occurredAt).toLocaleString("en-US", { dateStyle: "medium", timeStyle: "short", timeZone: "UTC" })} UTC</td><td className="capitalize">{event.status}</td></tr>)}</tbody></table></div></section>
  </main></>;
}
function ExplanationSection({ label, content }: { label: string; content: string | string[] }) { const entries = Array.isArray(content) ? content : [content]; return <div className="mt-5 border-t border-teal-800 pt-4"><h3 className="text-sm font-semibold text-teal-300">{label}</h3>{entries.map((item, index) => <p key={index} className="mt-2 text-sm leading-6 text-teal-50">{item}</p>)}</div>; }
