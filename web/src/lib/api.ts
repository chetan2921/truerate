import type { components } from "./api-types";

type Schemas = components["schemas"];
export type Analysis = Schemas["Analysis"];
export type AnalysisRequest = Schemas["AnalysisRequest"];
export type AnalysisSummary = Schemas["AnalysisSummary"];
export type Report = Schemas["Report"];
export type Meta = Schemas["Meta"];

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function call<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(BASE + path, { ...init, headers: { "Content-Type": "application/json" }, cache: "no-store" });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(typeof body.detail === "string" ? body.detail : `The API answered ${res.status}.`);
  }
  return res.json();
}

export const api = {
  createAnalysis: (req: AnalysisRequest) => call<Schemas["Created"]>("/api/analyses", { method: "POST", body: JSON.stringify(req) }),
  getAnalysis: (id: string) => call<Analysis>(`/api/analyses/${id}`),
  listAnalyses: () => call<AnalysisSummary[]>("/api/analyses"),
  meta: () => call<Meta>("/api/meta"),
};
