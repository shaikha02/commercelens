export type Severity = "warning" | "critical";
export interface Finding { id: string; severity: Severity; title: string; evidence: string; recommendation: string; }
