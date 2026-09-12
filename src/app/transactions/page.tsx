"use client";
import { useMemo, useState } from "react";
import Link from "next/link";
import { Header, SeverityBadge } from "@/components/ui";
import { transactions } from "@/modules/transactions/data";
import { reconcileTransaction } from "@/modules/reconciliation/rules";
import { systems } from "@/modules/transactions/types";

export default function TransactionsPage() {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("all");
  const [system, setSystem] = useState("all");
  const rows = useMemo(() => transactions.map((transaction) => {
    const findings = reconcileTransaction(transaction);
    const state: "healthy" | "warning" | "critical" = findings.some((f) => f.severity === "critical") ? "critical" : findings.length ? "warning" : "healthy";
    return { transaction, findings, state };
  }).filter(({ transaction, state }) => {
    const needle = query.toLowerCase();
    return (status === "all" || state === status) && (system === "all" || transaction.events.some((event) => event.system === system)) && (!needle || `${transaction.invoiceNumber} ${transaction.customer} ${transaction.events.map((event) => event.reference).join(" ")}`.toLowerCase().includes(needle));
  }), [query, status, system]);
  return <><Header /><main className="mx-auto max-w-7xl px-6 py-10">
    <p className="eyebrow">Transaction explorer</p><h1 className="mt-2 text-3xl font-semibold tracking-tight">Find an investigation</h1>
    <div className="panel mt-7 grid gap-3 md:grid-cols-[1fr_160px_160px]">
      <label className="sr-only" htmlFor="search">Search transactions</label><input id="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search invoice, customer, or source reference" />
      <label className="sr-only" htmlFor="status">Status</label><select id="status" value={status} onChange={(event) => setStatus(event.target.value)}><option value="all">All statuses</option><option value="healthy">Healthy</option><option value="warning">Warning</option><option value="critical">Broken</option></select>
      <label className="sr-only" htmlFor="system">System evidence</label><select id="system" value={system} onChange={(event) => setSystem(event.target.value)}><option value="all">All systems</option>{systems.map((item) => <option key={item}>{item}</option>)}</select>
    </div>
    <p className="mt-5 text-sm text-slate-500">{rows.length} of {transactions.length} transactions</p>
    <div className="panel mt-3 overflow-x-auto p-0"><table><thead><tr><th>Invoice</th><th>Customer</th><th>Amount</th><th>Lineage</th><th>Status</th><th><span className="sr-only">Open</span></th></tr></thead><tbody>{rows.map(({ transaction, state, findings }) => <tr key={transaction.id}><td className="font-semibold">{transaction.invoiceNumber}<br /><span className="text-xs font-normal text-slate-400">{transaction.createdAt.slice(0, 10)}</span></td><td>{transaction.customer}</td><td>{transaction.currency} {transaction.invoiceTotal.toLocaleString()}</td><td><span className="text-sm text-slate-500">{transaction.events.length}/6 events</span></td><td><SeverityBadge severity={state} />{findings.length > 0 && <span className="ml-2 text-xs text-slate-400">{findings.length} finding{findings.length > 1 ? "s" : ""}</span>}</td><td><Link className="text-sm font-semibold text-teal-700" href={`/transactions/${transaction.id}`}>Investigate →</Link></td></tr>)}</tbody></table></div>
  </main></>;
}
