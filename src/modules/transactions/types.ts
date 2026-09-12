export const systems = ["Invoice", "AR", "GL", "Revenue", "Tax", "Receipt"] as const;
export type System = (typeof systems)[number];
export type EventStatus = "posted" | "pending" | "failed";
export interface TransactionEvent { id: string; system: System; status: EventStatus; occurredAt: string; reference: string; amount: number; currency: string; description: string; }
export interface Transaction { id: string; invoiceNumber: string; customer: string; invoiceTotal: number; currency: string; taxable: boolean; createdAt: string; events: TransactionEvent[]; }
