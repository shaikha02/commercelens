import Link from "next/link";
import type { Severity } from "@/modules/reconciliation/types";

export function Header() {
  return <header className="border-b border-slate-200 bg-white/80 backdrop-blur"><nav className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6" aria-label="Main navigation"><Link href="/" className="flex items-center gap-2 font-semibold tracking-tight"><span className="grid h-8 w-8 place-items-center rounded-lg bg-teal-600 text-sm text-white">C</span>CommerceLens</Link><div className="flex gap-5 text-sm font-medium text-slate-600"><Link href="/" className="hover:text-slate-950">Overview</Link><Link href="/transactions" className="hover:text-slate-950">Transactions</Link></div></nav></header>;
}

export function SeverityBadge({ severity }: { severity: Severity | "healthy" }) {
  const text = severity === "critical" ? "Broken" : severity === "warning" ? "Warning" : "Healthy";
  const styles = severity === "critical" ? "bg-rose-50 text-rose-700 ring-rose-200" : severity === "warning" ? "bg-amber-50 text-amber-700 ring-amber-200" : "bg-emerald-50 text-emerald-700 ring-emerald-200";
  return <span className={`shrink-0 rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset ${styles}`}>{text}</span>;
}
