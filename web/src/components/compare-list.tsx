"use client";

import { ExternalLink } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { api } from "@/lib/api";

// Accounts as a tick list: each can be priced alone, or ticked and compared in one batch.
// `include` is a creator who goes first in the comparison without being in the list (the report's own creator).
export default function CompareList({ handles, include, category, budget, instagramLinks }: {
  handles: string[];
  include?: string;
  category?: string | null;
  budget?: number | null;
  instagramLinks?: boolean;
}) {
  const router = useRouter();
  const [starting, setStarting] = useState("");
  const [picked, setPicked] = useState<string[]>([]);
  const [comparing, setComparing] = useState(false);
  const busy = Boolean(starting) || comparing;

  async function analyse(handle: string) {
    setStarting(handle);
    try {
      const { id } = await api.createAnalysis({ handle, category: category ?? null, budget: budget ?? null });
      router.push(`/analyses/${id}`);
    } catch {
      setStarting("");
    }
  }

  async function compare() {
    setComparing(true);
    try {
      const { id } = await api.createBatch({ handles: include ? [include, ...picked] : picked, category: category ?? null, budget: budget ?? null });
      router.push(`/batch/${id}`);
    } catch {
      setComparing(false);
    }
  }

  const all = picked.length === handles.length;
  const count = picked.length + (include ? 1 : 0);

  return (
    <>
      <div className="mt-4 flex flex-wrap items-center gap-3">
        <button type="button" className="btn btn-primary" disabled={busy || picked.length === 0} onClick={compare}>
          {comparing ? "Starting…" : count > 1 ? `Compare ${count} creators` : "Compare creators"}
        </button>
        <button type="button" className="btn btn-quiet" disabled={busy} onClick={() => setPicked(all ? [] : handles)}>
          {all ? "Clear all" : "Select all"}
        </button>
      </div>
      <ul className="mt-3 divide-y divide-line">
        {handles.map((h) => (
          <li key={h} className="flex items-center justify-between gap-4 py-2">
            <span className="flex min-w-0 items-center gap-3">
              <label className="flex cursor-pointer items-center gap-3">
                <input type="checkbox" className="h-4 w-4 accent-accent" checked={picked.includes(h)} disabled={busy}
                  onChange={(e) => setPicked(e.target.checked ? [...picked, h] : picked.filter((x) => x !== h))} />
                @{h}
              </label>
              {instagramLinks && (
                <a href={`https://www.instagram.com/${h}/`} target="_blank" rel="noreferrer" aria-label={`Open @${h} on Instagram`} title="Open on Instagram"
                  className="text-muted hover:text-text">
                  <ExternalLink size={14} aria-hidden />
                </a>
              )}
            </span>
            <button type="button" className="btn btn-quiet px-3 py-1.5 text-sm font-normal" disabled={busy} onClick={() => analyse(h)} aria-label={`Price @${h} alone`}>
              {starting === h ? "Starting…" : "Price"}
            </button>
          </li>
        ))}
      </ul>
    </>
  );
}
