"use client";

import { Plus, X } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useLayoutEffect, useRef, useState } from "react";

import ProductOptions from "@/components/product-options";
import { api, type BatchSummary, type Meta } from "@/lib/api";
import { daysAgo } from "@/lib/format";

const MAX = 50;

type Row = { id: number; value: string };

export default function BatchPage() {
  const router = useRouter();
  const nextId = useRef(1);
  const inputs = useRef(new Map<number, HTMLInputElement>());
  const [rows, setRows] = useState<Row[]>([{ id: 0, value: "" }]);
  const pendingFocus = useRef<number | null>(null);
  const [category, setCategory] = useState("");
  const [budget, setBudget] = useState("");
  const [meta, setMeta] = useState<Meta | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [recent, setRecent] = useState<BatchSummary[] | null>(null);
  const handles = rows.map((r) => r.value.trim()).filter(Boolean);

  useEffect(() => {
    api.meta().then(setMeta).catch(() => setMeta(null));
  }, []);

  // Runs again each time this page is shown, so a batch started a moment ago is listed with its progress.
  useEffect(() => {
    api.listBatches().then(setRecent).catch(() => setRecent([]));
  }, []);

  // Next keeps this page alive, hidden, while a batch runs. Coming back must show a fresh form, not "Starting…"
  // with the last creators; the product and budget stay.
  useLayoutEffect(
    () => () => {
      setBusy(false);
      setRows([{ id: nextId.current++, value: "" }]);
    },
    [],
  );

  // Focus a row once React has rendered it.
  useEffect(() => {
    if (pendingFocus.current === null) return;
    inputs.current.get(pendingFocus.current)?.focus();
    pendingFocus.current = null;
  });

  function newRow(value = ""): Row {
    return { id: nextId.current++, value };
  }

  function show(list: Row[], focus: number) {
    pendingFocus.current = focus;
    setRows(list);
  }

  function addRow() {
    const added = newRow();
    show([...rows, added], added.id);
  }

  function update(id: number, value: string) {
    setRows(rows.map((r) => (r.id === id ? { ...r, value } : r)));
  }

  function remove(id: number) {
    const i = rows.findIndex((r) => r.id === id);
    const rest = rows.filter((r) => r.id !== id);
    if (rest.length === 0) {
      const empty = newRow();
      show([empty], empty.id);
    } else show(rest, rest[Math.max(0, i - 1)].id);
  }

  function onKeyDown(e: React.KeyboardEvent<HTMLInputElement>, row: Row, i: number) {
    if (e.key === "Enter") {
      e.preventDefault(); // Enter moves to the next creator; the button starts the batch
      if (!row.value.trim()) return;
      if (i < rows.length - 1) inputs.current.get(rows[i + 1].id)?.focus();
      else if (rows.length < MAX) addRow();
    } else if (e.key === "Backspace" && !row.value && rows.length > 1) {
      e.preventDefault();
      remove(row.id);
    }
  }

  // A pasted list (one per line, or separated by commas or spaces) fills this row and the ones after it.
  function onPaste(e: React.ClipboardEvent<HTMLInputElement>, row: Row, i: number) {
    const parts = e.clipboardData.getData("text").split(/[\s,]+/).filter(Boolean);
    if (parts.length < 2) return;
    e.preventDefault();
    const added = parts.slice(1, MAX - rows.length + 1).map((v) => newRow(v));
    show([...rows.slice(0, i), { ...row, value: parts[0] }, ...added, ...rows.slice(i + 1)], (added.at(-1) ?? row).id);
  }

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
      <form onSubmit={submit} className="mt-6 grid max-w-4xl items-start gap-6 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
        <fieldset className="flex min-w-0 flex-col gap-2">
          <legend className="basis mb-1">Creators, up to {MAX}. Type a handle or profile link and press Enter for the next one.</legend>
          <ol className="flex flex-col gap-2">
            {rows.map((row, i) => (
              <li key={row.id} className="flex items-center gap-3">
                <span className="figure basis w-6 shrink-0 text-right" aria-hidden>
                  {i + 1}.
                </span>
                <input
                  ref={(el) => {
                    if (el) inputs.current.set(row.id, el);
                    else inputs.current.delete(row.id);
                  }}
                  aria-label={`Creator ${i + 1}`}
                  className="field min-w-0 flex-1"
                  placeholder={i === 0 ? "@handle or instagram.com/handle" : ""}
                  value={row.value}
                  onChange={(e) => update(row.id, e.target.value)}
                  onKeyDown={(e) => onKeyDown(e, row, i)}
                  onPaste={(e) => onPaste(e, row, i)}
                  autoComplete="off"
                  spellCheck={false}
                  autoFocus={i === 0}
                />
                <button type="button" onClick={() => remove(row.id)} aria-label={`Remove creator ${i + 1}`} title="Remove"
                  className={`shrink-0 rounded-md p-2 text-muted transition-colors duration-150 hover:bg-surface hover:text-text ${rows.length === 1 && !row.value ? "invisible" : ""}`}>
                  <X size={16} aria-hidden />
                </button>
              </li>
            ))}
          </ol>
          {rows.length < MAX && (
            <button type="button" className="btn btn-quiet ml-9 self-start py-2 text-sm" onClick={addRow}>
              <Plus size={16} aria-hidden />
              Add creator
            </button>
          )}
        </fieldset>
        <div className="flex flex-col gap-4">
          <label className="basis flex flex-col gap-1">
            Product category, optional
            <select className="field text-sm text-text" value={category} onChange={(e) => setCategory(e.target.value)}>
              <option value="">Any</option>
              {meta && <ProductOptions products={meta.products} categories={meta.categories} />}
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

      {recent && recent.length > 0 && (
        <section aria-labelledby="recent-batches" className="mt-16 max-w-4xl">
          <h2 id="recent-batches" className="section-title">
            Recent batches
          </h2>
          <ul className="mt-3 divide-y divide-line">
            {recent.map((b) => {
              const running = b.done < b.total;
              return (
                <li key={b.id}>
                  <Link href={`/batch/${b.id}`} className="grid grid-cols-[1fr_auto_6rem] items-center gap-6 py-3 no-underline hover:bg-surface">
                    <span className="truncate">
                      {b.handles.slice(0, 3).map((h) => `@${h}`).join(", ")}
                      {b.handles.length > 3 && <span className="basis"> and {b.handles.length - 3} more</span>}
                    </span>
                    <span className={`figure text-sm ${running ? "text-text" : "text-muted"}`}>{running ? `Running, ${b.done} of ${b.total} done` : `${b.total} done`}</span>
                    <span className="basis text-right">{daysAgo(b.created_at)}</span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </section>
      )}
    </main>
  );
}
