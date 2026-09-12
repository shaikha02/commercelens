import { describe, expect, it } from "vitest";
import { transactions } from "@/modules/transactions/data";
import { reconcileTransaction } from "@/modules/reconciliation/rules";
import { createExplanation } from "./explanation";

describe("createExplanation", () => {
  it("returns a no-action explanation for matching evidence", () => {
    expect(createExplanation(transactions[0], []).action).toContain("No action required");
  });

  it("grounds the explanation in reconciliation findings", () => {
    const transaction = transactions[3];
    const explanation = createExplanation(transaction, reconcileTransaction(transaction));
    expect(explanation.evidence).toContainEqual(expect.stringContaining("no GL event"));
    expect(explanation.action).toContainEqual(expect.stringContaining("posting queue"));
  });
});
