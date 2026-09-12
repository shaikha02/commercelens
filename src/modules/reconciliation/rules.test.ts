import { describe, expect, it } from "vitest";
import { transactions } from "@/modules/transactions/data";
import { reconcileTransaction } from "./rules";

describe("reconcileTransaction", () => {
  it("returns no findings for a complete matching transaction", () => {
    expect(reconcileTransaction(transactions[0])).toEqual([]);
  });
  it("detects each seeded reconciliation exception", () => {
    expect(reconcileTransaction(transactions[3]).map((finding) => finding.id)).toContain("ar-without-gl");
    expect(reconcileTransaction(transactions[4]).map((finding) => finding.id)).toContain("revenue-mismatch");
    expect(reconcileTransaction(transactions[5]).map((finding) => finding.id)).toContain("missing-tax");
    expect(reconcileTransaction(transactions[6]).map((finding) => finding.id)).toContain("receipt-balance-mismatch");
    expect(reconcileTransaction(transactions[7]).map((finding) => finding.id)).toContain("missing-receipt");
  });
});
