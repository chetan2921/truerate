"use client";

import { ChevronDown, X } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { CallChip } from "@/components/chips";
import ProductOptions from "@/components/product-options";
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
  const [showAll, setShowAll] = useState(false);

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
    <main className="mx-auto max-w-6xl px-6 pb-24">
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

      <section className="mx-auto mt-20 max-w-4xl" aria-labelledby="recent">
        <h2 id="recent" className="section-title">
          Recent analyses
        </h2>
        {recent === null ? (
          <p className="basis mt-3">Loading…</p>
        ) : recent.length === 0 ? (
          <p className="basis mt-3">No creators priced yet. Paste a handle above to start.</p>
        ) : (
          <>
            <ul className="mt-3 divide-y divide-line">
              {(showAll ? recent : recent.slice(0, 10)).map((a) => (
                <li key={a.id} className="flex items-center gap-2">
                  <Link href={`/analyses/${a.id}`} className="grid min-w-0 flex-1 grid-cols-[1fr_auto_auto] items-center gap-4 py-3 no-underline hover:bg-surface sm:grid-cols-[1fr_9rem_11rem_6rem_4rem]">
                    <span className="truncate font-semibold">@{a.handle}</span>
                    <span className="hidden basis sm:block">{a.verdict ?? (a.status === "running" ? "Running" : a.status === "failed" ? "Failed" : "Out of scope")}</span>
                    <span className="figure whitespace-nowrap text-right">{a.low != null && a.high != null ? `${inr(a.low)} to ${inr(a.high)}` : ""}</span>
                    <span className="text-right">{a.call && <CallChip call={a.call} />}</span>
                    <span className="basis hidden text-right sm:block">{daysAgo(a.created_at)}</span>
                  </Link>
                  <button type="button" onClick={() => remove(a.id)} aria-label={`Remove @${a.handle} from recent analyses`} title="Remove from this list"
                    className="rounded-md p-2 text-muted transition-colors duration-150 hover:bg-surface hover:text-text">
                    <X size={16} aria-hidden />
                  </button>
                </li>
              ))}
            </ul>
            {recent.length > 10 && (
              <button type="button" className="btn btn-quiet mt-4 py-2 text-sm" aria-expanded={showAll} onClick={() => setShowAll((v) => !v)}>
                {showAll ? "Show the latest 10" : `Show all ${recent.length}`}
                <ChevronDown size={16} aria-hidden className={`transition-transform duration-150 ${showAll ? "rotate-180" : ""}`} />
              </button>
            )}
          </>
        )}
      </section>
    </main>
  );
}
