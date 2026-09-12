import type { Transaction } from "@/modules/transactions/types";
import type { Finding } from "./types";

const find = (transaction: Transaction, system: string) => transaction.events.find((event) => event.system === system);

function checkArWithoutGl(transaction: Transaction): Finding | null {
  const ar = find(transaction, "AR");
  if (!ar || find(transaction, "GL")) return null;
  return { id: "ar-without-gl", severity: "critical", title: "AR posted but GL journal is missing", evidence: `AR reference ${ar.reference} for ${transaction.currency} ${ar.amount.toLocaleString()} exists; no GL event was recorded.`, recommendation: "Review the AR-to-GL posting queue and create or replay the missing journal." };
}

function checkRevenueMismatch(transaction: Transaction): Finding | null {
  const revenue = find(transaction, "Revenue");
  if (!revenue || revenue.amount === transaction.invoiceTotal) return null;
  return { id: "revenue-mismatch", severity: "critical", title: "Invoice total differs from recognized revenue", evidence: `Invoice is ${transaction.currency} ${transaction.invoiceTotal.toLocaleString()}; revenue reference ${revenue.reference} is ${transaction.currency} ${revenue.amount.toLocaleString()}.`, recommendation: "Validate the recognition schedule and post a correcting revenue entry." };
}

function checkMissingTax(transaction: Transaction): Finding | null {
  if (!transaction.taxable || find(transaction, "Tax")) return null;
  return { id: "missing-tax", severity: "warning", title: "Taxable transaction has no filing event", evidence: `Invoice ${transaction.invoiceNumber} is marked taxable but no Tax evidence was found.`, recommendation: "Confirm tax determination, then submit or record the required filing." };
}

function checkMissingReceipt(transaction: Transaction): Finding | null {
  const ar = find(transaction, "AR");
  if (!ar || find(transaction, "Receipt")) return null;
  return { id: "missing-receipt", severity: "warning", title: "AR balance has no receipt event", evidence: `AR reference ${ar.reference} remains unsupported by a Receipt event for ${transaction.currency} ${ar.amount.toLocaleString()}.`, recommendation: "Confirm whether payment was received and post or import the receipt evidence." };
}

function checkReceiptBalance(transaction: Transaction): Finding | null {
  const receipt = find(transaction, "Receipt");
  if (!receipt || receipt.amount === transaction.invoiceTotal) return null;
  return { id: "receipt-balance-mismatch", severity: "warning", title: "Receipt does not match outstanding balance", evidence: `Receipt ${receipt.reference} is ${transaction.currency} ${receipt.amount.toLocaleString()} against an invoice balance of ${transaction.currency} ${transaction.invoiceTotal.toLocaleString()}.`, recommendation: "Apply the remaining balance or investigate the partial-payment and remittance record." };
}

export function reconcileTransaction(transaction: Transaction): Finding[] {
  return [checkArWithoutGl, checkRevenueMismatch, checkMissingTax, checkMissingReceipt, checkReceiptBalance]
    .map((rule) => rule(transaction))
    .filter((finding): finding is Finding => finding !== null);
}
