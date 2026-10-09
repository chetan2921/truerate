"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { api, type Meta } from "@/lib/api";

export default function BatchPage() {
  const router = useRouter();
  const [text, setText] = useState("");
  const [category, setCategory] = useState("");
  const [budget, setBudget] = useState("");
  const [meta, setMeta] = useState<Meta | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const handles = text.split(/[\s,]+/).filter(Boolean);

  useEffect(() => {
    api.meta().then(setMeta).catch(() => setMeta(null));
  }, []);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const { id } = await api.createBatch({ handles, category: category || null, budget: budget ? Number(budget) : null });
      router.push(`/batch/${id}`);
    } catch (err) {
      setError((err as Error).message);
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto max-w-6xl px-6 pb-24 pt-[min(6vh,3rem)]">
      <h1 className="text-3xl font-bold">Shortlist several creators</h1>
      <p className="basis mt-2 max-w-2xl">Each creator gets the full analysis. The table ranks them by what one reel costs per 1,000 views.</p>
      <form onSubmit={submit} className="mt-6 grid max-w-4xl gap-4 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
        <label className="flex flex-col gap-1">
          <span className="basis">Handles or profile links, one per line, up to 50</span>
          <textarea className="field min-h-56 font-sans" value={text} onChange={(e) => setText(e.target.value)} placeholder={"@first.creator\ninstagram.com/second.creator"} spellCheck={false} />
        </label>
        <div className="flex flex-col gap-4">
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
            Budget per reel in ₹, optional
            <input className="field text-sm" inputMode="numeric" placeholder="50000" value={budget} onChange={(e) => setBudget(e.target.value.replace(/\D/g, ""))} />
          </label>
          <button type="submit" className="btn btn-primary justify-center" disabled={busy || handles.length === 0}>
            {busy ? "Starting…" : handles.length ? `Price ${handles.length} creator${handles.length === 1 ? "" : "s"}` : "Price creators"}
          </button>
          {error && (
            <p role="alert" className="text-avoid">
              {error}
            </p>
          )}
        </div>
      </form>
    </main>
  );
}
