"use client";

import Link from "next/link";
import { use, useEffect, useState } from "react";

import { CallChip } from "@/components/chips";
import { api, type Batch } from "@/lib/api";
import { compact, inr } from "@/lib/format";

function toCsv(b: Batch): string {
  const head = ["rank", "handle", "decision", "verdict", "recommended_inr", "low_inr", "high_inr", "inr_per_1000_views", "expected_views", "status"];
  const rows = b.rows.map((r, i) => [i + 1, r.handle, r.call ?? "", r.verdict ?? "", r.fair ?? "", r.low ?? "", r.high ?? "", r.cost_per_1k ?? "", r.expected_views ?? "", r.status]);
  return [head, ...rows].map((r) => r.map((x) => `"${String(x).replace(/"/g, '""')}"`).join(",")).join("\n");
}

export default function BatchView({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [batch, setBatch] = useState<Batch | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let stopped = false;
    let timer: ReturnType<typeof setTimeout>;
    const load = async () => {
      try {
        const next = await api.getBatch(id);
        if (stopped) return;
        setBatch(next);
        if (next.done < next.total) timer = setTimeout(load, 2000);
      } catch (e) {
        if (!stopped) setError((e as Error).message);
      }
    };
    load();
    return () => {
      stopped = true;
      clearTimeout(timer);
    };
  }, [id]);

  function exportCsv() {
    if (!batch) return;
    const url = URL.createObjectURL(new Blob([toCsv(batch)], { type: "text/csv" }));
    const a = Object.assign(document.createElement("a"), { href: url, download: `truerate-shortlist-${id}.csv` });
    a.click();
    URL.revokeObjectURL(url);
  }

  if (error) return <main className="mx-auto max-w-6xl px-6 pt-10"><h1 className="text-3xl font-bold">Couldn&apos;t load this shortlist</h1><p className="mt-3">{error}</p></main>;
  if (!batch) return <main className="mx-auto max-w-6xl px-6 pt-10 text-3xl font-bold">Loading…</main>;
  const budget = batch.inputs.budget;

  return (
    <main className="mx-auto max-w-6xl px-6 pb-24 pt-4">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-3xl font-bold">Shortlist of {batch.total}</h1>
          <p className="basis mt-1">
            {batch.done < batch.total ? `${batch.done} of ${batch.total} done; the table fills in as each finishes.` : "All done."} Cheapest views first
            {batch.inputs.category ? ` · for ${batch.inputs.category}` : ""}
            {budget ? ` · budget ${inr(budget)}` : ""}.
          </p>
        </div>
        <button type="button" className="btn btn-quiet" onClick={exportCsv} disabled={batch.done === 0}>
          Export CSV
        </button>
      </div>
      <div className="mt-6 overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-bg text-left text-muted">
            <tr>
              <th className="py-2 pr-3 font-normal">#</th>
              <th className="py-2 pr-3 font-normal">Creator</th>
              <th className="py-2 pr-3 font-normal">Decision</th>
              <th className="py-2 pr-3 font-normal">Audience</th>
              <th className="py-2 pr-3 text-right font-normal">Recommended</th>
              <th className="py-2 pr-3 text-right font-normal">Per 1,000 views</th>
              <th className="py-2 text-right font-normal">Expected views</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {batch.rows.map((r, i) => (
              <tr key={r.analysis_id}>
                <td className="figure py-2.5 pr-3 text-muted">{r.cost_per_1k != null ? i + 1 : ""}</td>
                <td className="py-2.5 pr-3">
                  <Link href={`/analyses/${r.analysis_id}`}>@{r.handle}</Link>
                </td>
                {r.status === "done" ? (
                  <>
                    <td className="py-2.5 pr-3">{r.call && <CallChip call={r.call} />}</td>
                    <td className="py-2.5 pr-3">{r.verdict}</td>
                    <td className="figure py-2.5 pr-3 text-right">
                      {r.fair != null && inr(r.fair)}
                      {budget && r.fair != null && r.fair > budget && <span className="block text-xs text-negotiate">over budget</span>}
                    </td>
                    <td className="figure py-2.5 pr-3 text-right">{r.cost_per_1k != null && inr(r.cost_per_1k)}</td>
                    <td className="figure py-2.5 text-right">{r.expected_views != null && compact(r.expected_views)}</td>
                  </>
                ) : (
                  <td colSpan={5} className="basis py-2.5">
                    {r.status === "running" ? "Running…" : r.reason ?? r.status}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}
