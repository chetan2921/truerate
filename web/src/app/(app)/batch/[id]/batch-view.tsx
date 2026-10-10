"use client";

import { use, useEffect, useState } from "react";

import { PriceChart, ReachChart, Recommendation, Scorecard } from "@/components/batch/compare";
import { api, type Batch } from "@/lib/api";
import { inr } from "@/lib/format";

function toCsv(b: Batch): string {
  const head = ["rank", "handle", "decision", "pay_about_inr", "likely_low_inr", "likely_high_inr", "low_inr", "high_inr", "inr_per_1000_views", "expected_views", "verdicts", "status"];
  const rows = b.rows.map((r, i) => [i + 1, r.handle, r.call ?? "", r.fair ?? "", r.likely_low ?? "", r.likely_high ?? "", r.low ?? "", r.high ?? "", r.cost_per_1k ?? "",
    r.expected_views ?? "", r.outputs.map((o) => o.title).join("; "), r.status]);
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
            {batch.done < batch.total ? `${batch.done} of ${batch.total} done; this fills in as each finishes.` : "All done."} Who to book, then the details
            {batch.inputs.category ? ` · for ${batch.inputs.category}` : ""}
            {budget ? ` · budget ${inr(budget)}` : ""}.
          </p>
        </div>
        <button type="button" className="btn btn-quiet" onClick={exportCsv} disabled={batch.done === 0}>
          Export CSV
        </button>
      </div>
      <div className="mt-6">
        <Recommendation rows={batch.rows} />
      </div>
      {/* Gaps follow weight: the dense scorecard gets room, the three bar charts sit closer together. */}
      <section aria-labelledby="side-by-side" className="pt-12">
        <h2 id="side-by-side" className="section-title">
          Side by side
        </h2>
        <p className="basis mt-1">Hover an answer for the reason. Cheapest views first; Avoid goes last.</p>
        <div className="mt-4">
          <Scorecard rows={batch.rows} />
        </div>
      </section>
      <div className="grid gap-x-16 gap-y-12 pt-16 xl:grid-cols-2">
        <PriceChart rows={batch.rows} budget={budget} />
        <ReachChart rows={batch.rows} />
      </div>
    </main>
  );
}
