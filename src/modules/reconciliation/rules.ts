import type { Transaction } from "@/modules/transactions/types";
import type { Finding } from "./types";

const find = (transaction: Transaction, system: string) => transaction.events.find((event) => event.system === system);
export function reconcileTransaction(transaction: Transaction): Finding[] {
  const findings: Finding[] = [];
  const ar = find(transaction, "AR"), gl = find(transaction, "GL"), revenue = find(transaction, "Revenue"), tax = find(transaction, "Tax"), receipt = find(transaction, "Receipt");
  if (ar && !gl) findings.push({ id: "ar-without-gl", severity: "critical", title: "AR posted but GL journal is missing", evidence: `AR reference ${ar.reference} for ${transaction.currency} ${ar.amount.toLocaleString()} exists; no GL event was recorded.`, recommendation: "Review the AR-to-GL posting queue and create or replay the missing journal." });
  if (revenue && revenue.amount !== transaction.invoiceTotal) findings.push({ id: "revenue-mismatch", severity: "critical", title: "Invoice total differs from recognized revenue", evidence: `Invoice is ${transaction.currency} ${transaction.invoiceTotal.toLocaleString()}; revenue reference ${revenue.reference} is ${transaction.currency} ${revenue.amount.toLocaleString()}.`, recommendation: "Validate the recognition schedule and post a correcting revenue entry." });
  if (transaction.taxable && !tax) findings.push({ id: "missing-tax", severity: "warning", title: "Taxable transaction has no filing event", evidence: `Invoice ${transaction.invoiceNumber} is marked taxable but no Tax evidence was found.`, recommendation: "Confirm tax determination, then submit or record the required filing." });
  if (receipt && receipt.amount !== transaction.invoiceTotal) findings.push({ id: "receipt-balance-mismatch", severity: "warning", title: "Receipt does not match outstanding balance", evidence: `Receipt ${receipt.reference} is ${transaction.currency} ${receipt.amount.toLocaleString()} against an invoice balance of ${transaction.currency} ${transaction.invoiceTotal.toLocaleString()}.`, recommendation: "Apply the remaining balance or investigate the partial-payment and remittance record." });
  return findings;
}
