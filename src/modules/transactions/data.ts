import type { Transaction } from "./types";
const eventTimestamp = (index: number) => `2026-09-${String(index + 2).padStart(2, "0")}T10:30:00Z`;
const event = (id: string, system: Transaction["events"][number]["system"], amount: number, reference: string, index: number, status: Transaction["events"][number]["status"] = "posted") => ({ id, system, amount, currency: "USD", reference, status, occurredAt: eventTimestamp(index), description: `${system} ${status}` });
const lifecycle = (id: string, total: number) => ["Invoice", "AR", "GL", "Revenue", "Tax", "Receipt"].map((system, index) => event(`${id}-${index}`, system as Transaction["events"][number]["system"], total, `${system.slice(0, 2).toUpperCase()}-${id}`, index));
const complete = (id: string, total: number, customer: string): Transaction => ({ id, invoiceNumber: `INV-2026-${id.padStart(4, "0")}`, customer, invoiceTotal: total, currency: "USD", taxable: true, createdAt: "2026-09-02T09:00:00Z", events: lifecycle(id, total) });
const alpine = complete("1004", 3200, "Alpine Outfitters");
const blueYonder = complete("1005", 1500, "Blue Yonder");
const tailspin = complete("1006", 925, "Tailspin Toys");
const litware = complete("1007", 1800, "Litware");
export const transactions: Transaction[] = [
  complete("1001", 1240, "Northstar Goods"), complete("1002", 860, "Fabrikam Studio"), complete("1003", 2475, "Contoso Retail"),
  { ...alpine, events: alpine.events.filter((e) => e.system !== "GL") },
  { ...blueYonder, events: blueYonder.events.map((e) => e.system === "Revenue" ? { ...e, amount: 1350 } : e) },
  { ...tailspin, events: tailspin.events.filter((e) => e.system !== "Tax") },
  { ...litware, events: litware.events.map((e) => e.system === "Receipt" ? { ...e, amount: 1500 } : e) },
  { ...complete("1008", 640, "Adventure Works"), events: complete("1008", 640, "Adventure Works").events.filter((e) => e.system !== "Receipt") },
  complete("1009", 4320, "Woodgrove Bank"), complete("1010", 715, "Proseware"),
];
export const getTransaction = (id: string) => transactions.find((transaction) => transaction.id === id);
