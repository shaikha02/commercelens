import type { Transaction } from "@/modules/transactions/types";
import type { Finding } from "@/modules/reconciliation/types";
export function createExplanation(transaction: Transaction, findings: Finding[]) {
  if (!findings.length) return { evidence: `All six lifecycle systems have matching evidence for ${transaction.invoiceNumber}.`, rootCause: "No reconciliation exception was detected.", action: "No action required; retain this lineage for audit review." };
  return { evidence: findings.map((finding) => finding.evidence), rootCause: `The evidence indicates ${findings.map((finding) => finding.title.toLowerCase()).join("; ")}. This is a deterministic rule-based assessment, not a live AI inference.`, action: findings.map((finding) => finding.recommendation) };
}
