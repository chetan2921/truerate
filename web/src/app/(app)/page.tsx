"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { CallChip } from "@/components/chips";
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
      <section className="pt-[min(10vh,5rem)]">
        <h1 className="max-w-3xl font-bold leading-[1.05]" style={{ fontSize: "clamp(2.25rem, min(5vw, 9vh), 3.75rem)" }}>
          What is this creator&apos;s reel worth?
        </h1>
        <form onSubmit={submit} className="mt-8 max-w-3xl">
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
                {meta?.categories.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
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

      <section className="mt-20 max-w-3xl" aria-labelledby="recent">
        <h2 id="recent" className="section-title">
          Recent analyses
        </h2>
        {recent === null ? (
          <p className="basis mt-3">Loading…</p>
        ) : recent.length === 0 ? (
          <p className="basis mt-3">No creators priced yet. Paste a handle above to start.</p>
        ) : (
          <ul className="mt-3 divide-y divide-line">
            {recent.map((a) => (
              <li key={a.id}>
                <Link href={`/analyses/${a.id}`} className="grid grid-cols-[1fr_auto_auto] items-center gap-4 py-3 no-underline hover:bg-surface sm:grid-cols-[1fr_10rem_6rem_6rem_6rem]">
                  <span className="truncate font-semibold">@{a.handle}</span>
                  <span className="hidden basis sm:block">{a.verdict ?? (a.status === "running" ? "Running" : a.status === "failed" ? "Failed" : "Out of scope")}</span>
                  <span className="figure text-right">{a.fair ? inr(a.fair) : ""}</span>
                  <span className="text-right">{a.call && <CallChip call={a.call} />}</span>
                  <span className="basis hidden text-right sm:block">{daysAgo(a.created_at)}</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
