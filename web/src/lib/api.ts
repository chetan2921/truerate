import type { components } from "./api-types";

type Schemas = components["schemas"];
export type Analysis = Schemas["Analysis"];
export type AnalysisRequest = Schemas["AnalysisRequest"];
export type AnalysisSummary = Schemas["AnalysisSummary"];
export type Report = Schemas["Report"];
export type Meta = Schemas["Meta"];
export type QuoteCheck = Schemas["QuoteCheck"];
export type Batch = Schemas["Batch"];
export type BatchRequest = Schemas["BatchRequest"];
export type RateCard = Schemas["RateCard"];
export type ModelReport = Schemas["ModelReport"];

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
  checkQuote: (id: string, quote: number) => call<QuoteCheck>(`/api/analyses/${id}/quote`, { method: "POST", body: JSON.stringify({ quote }) }),
  createBatch: (req: BatchRequest) => call<Schemas["Created"]>("/api/batches", { method: "POST", body: JSON.stringify(req) }),
  getBatch: (id: string) => call<Batch>(`/api/batches/${id}`),
  rateCard: () => call<RateCard>("/api/rate-card"),
  modelReport: () => call<ModelReport>("/api/model-report"),
};
