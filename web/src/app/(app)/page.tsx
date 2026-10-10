"use client";

import { useRouter } from "next/navigation";
import { useEffect, useLayoutEffect, useState } from "react";

import { CallChip } from "@/components/chips";
import ProductOptions from "@/components/product-options";
import RecentTable, { NameHandle } from "@/components/recent-table";
import { api, type AnalysisSummary, type Meta } from "@/lib/api";
import { daysAgo, inr } from "@/lib/format";

export default function AnalyzePage() {
  const router = useRouter();
  const [handle, setHandle] = useState("");
  const [category, setCategory] = useState("");
  const [quote, setQuote] = useState("");
  const [budget, setBudget] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [meta, setMeta] = useState<Meta | null>(null);
  const [recent, setRecent] = useState<AnalysisSummary[] | null>(null);

  useEffect(() => {
    api.meta().then(setMeta).catch(() => setMeta(null));
    api.listAnalyses().then(setRecent).catch(() => setRecent([]));
  }, []);

  function remove(id: string) {
    setRecent((list) => list?.filter((a) => a.id !== id) ?? null);
    api.hideAnalysis(id).catch((err) => {
      setError((err as Error).message);
      api.listAnalyses().then(setRecent).catch(() => {});
    });
  }

  // Next keeps this page alive, hidden, while the report is open. Coming back must show a fresh form, not "Starting…"
  // with the last handle; the product and budget stay, since they usually carry over to the next creator.
  useLayoutEffect(
    () => () => {
      setBusy(false);
      setHandle("");
      setQuote("");
    },
    [],
  );

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!handle.trim()) return;
    setBusy(true);
    setError("");
    try {
      const { id } = await api.createAnalysis({
        handle,
        category: category || null,
        quote: quote ? Number(quote) : null,
        budget: budget ? Number(budget) : null,
      });
      router.push(`/analyses/${id}`);
    } catch (err) {
      setError((err as Error).message);
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto max-w-6xl px-6 pb-12">
      <section className="mx-auto max-w-4xl pt-[min(10vh,5rem)]">
        <h1 className="text-center font-bold leading-[1.05]" style={{ fontSize: "clamp(2.25rem, min(5vw, 9vh), 3.75rem)" }}>
          What is this creator&apos;s reel worth?
        </h1>
        <form onSubmit={submit} className="mt-10">
          <div className="flex flex-col gap-3 sm:flex-row">
            <label htmlFor="handle" className="sr-only">
              Instagram handle or profile link
            </label>
            <input
              id="handle"
              autoFocus
              className="field min-w-0 flex-1 py-4 text-lg"
              placeholder="@handle or instagram.com/handle"
              value={handle}
              onChange={(e) => setHandle(e.target.value)}
              autoComplete="off"
              spellCheck={false}
            />
            <button type="submit" className="btn btn-primary justify-center px-6 text-lg" disabled={busy}>
              {busy ? "Starting…" : "Price this creator"}
            </button>
          </div>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <label className="basis flex flex-col gap-1">
              Product category, optional
              <select className="field text-sm text-text" value={category} onChange={(e) => setCategory(e.target.value)}>
                <option value="">Any</option>
                {meta && <ProductOptions products={meta.products} categories={meta.categories} />}
              </select>
            </label>
            <label className="basis flex flex-col gap-1">
              Their quote in ₹, optional
              <input className="field text-sm" inputMode="numeric" placeholder="45000" value={quote} onChange={(e) => setQuote(e.target.value.replace(/\D/g, ""))} />
            </label>
            <label className="basis flex flex-col gap-1">
              Our budget in ₹, optional
              <input className="field text-sm" inputMode="numeric" placeholder="60000" value={budget} onChange={(e) => setBudget(e.target.value.replace(/\D/g, ""))} />
            </label>
          </div>
          {error && (
            <p role="alert" className="mt-3 text-avoid">
              {error}
            </p>
          )}
        </form>
      </section>

      <RecentTable
        className="mx-auto mt-12 max-w-5xl"
        title="Recent analyses"
        items={recent}
        href={(a) => `/analyses/${a.id}`}
        onRemove={remove}
        removeLabel={(a) => `Remove @${a.handle} from recent analyses`}
        empty="No creators priced yet. Paste a handle above to start."
        columns={[
          { label: "Creator", className: "w-[34%]", cell: (a) => <NameHandle name={a.name} handle={a.handle} /> },
          { label: "Audience", cell: (a) => <span className="basis">{a.verdict ?? (a.status === "running" ? "Running" : a.status === "failed" ? "Failed" : "Out of scope")}</span> },
          { label: "Fair range", className: "w-48 text-right", cell: (a) => <span className="figure">{a.low != null && a.high != null ? `${inr(a.low)} to ${inr(a.high)}` : ""}</span> },
          { label: "Call", className: "w-28 text-right", cell: (a) => a.call && <CallChip call={a.call} /> },
          { label: "When", className: "w-28 text-right", cell: (a) => <span className="basis">{daysAgo(a.created_at)}</span> },
        ]}
      />
    </main>
  );
}
